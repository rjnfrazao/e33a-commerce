from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Auctions, Bid, Comments, Watchlist
from .utils import auctionExist


def index(request):
    auctions = Auctions.objects.filter(active=True)
    return render(request, "auctions/index.html", {
        "auctions": auctions
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def auctions_add(request):

    if request.method == "POST":

        auction = Auctions(
            id_category=Category.objects.get(
                id_category=request.POST["id_category"]),
            id_user=request.user,
            title=request.POST["title"],
            description=request.POST["description"],
            start_bid=request.POST["start_bid"],
            image_url=request.POST["image_url"],
            active=request.POST["active"]
        )
        auction.save()
        print("Saved Auction: ", auction.id_auction)
        return HttpResponseRedirect(reverse("auctions_item",
                                            args=[auction.id_auction]))
    else:
        return render(request, "auctions/auctionsAdd.html", {
            "categories": Category.objects.all()
        })


def auctions_item(request, id_auction):

    # Check if the auction exist.
    try:
        auction = Auctions.objects.get(id_auction=id_auction)
        error_message = ""
    except Auctions.DoesNotExist:
        # If not display an error message
        error_message = "This Auction Does Not Exist!"
        return render(request, "auctions/auctionsItem.html", {
            "error_message": error_message
        })

    # Here just because I can´t get the user id from the auction object.
    auctionUser = User.objects.get(username=auction.id_user)

    # Check if the auction is in the user´s watchlist.
    try:
        Watchlist.objects.get(id_auction=id_auction, id_user=request.user)
        watchlist = True
    except Watchlist.DoesNotExist:
        watchlist = False

    # Check if the auction's user is the one which created the auction
    if auctionUser.id == request.user.id:
        owner = True
    else:
        owner = False

    return render(request, "auctions/auctionsItem.html", {
        "auction": auction,
        "user": auction.id_user,
        "category": auction.id_category,
        "watchlist": watchlist,
        "auction_owner": owner
    })


def auctions_close(request, id_auction):
    auction = Auctions.objects.get(id_auction=id_auction)

    # TO DO

    # return render(request, "auctions/auctionsItem.html", {
    #    "auction": auction,
    #    "user": auction.id_user,
    #    "category": auction.id_category
    # })


def auctions_bid(request, id_auction):
    auction = Auctions.objects.get(id_auction=id_auction)

    # TO DO

    # return render(request, "auctions/auctionsItem.html", {
    #    "auction": auction,
    #    "user": auction.id_user,
    #    "category": auction.id_category
    # })


def auctions_oper(request, oper, id_auction):

    # REMOVE FROM UTILS auction = utils.auctionExist(id_auction)

    # Check if the auction exist.
    try:
        auction = Auctions.objects.get(id_auction=id_auction)

        if oper == "Add":

            watchlist = Watchlist(
                id_auction=Auctions.objects.get(id_auction=id_auction),
                id_user=User.objects.get(id=request.user.id)
            )

            try:
                watchlist.save()
                alert_message = "Item added to the watchlist."

            except:
                # Auction not saved
                print(
                    f"Log -> Error adding watchlist: {id_auction} and user:{request.user.id}")
                alert_message = "Watch list item duplicated."

        elif oper == "Delete":

            watchlist = Watchlist.objects.get(
                id_auction=Auctions.objects.get(id_auction=id_auction),
                id_user=User.objects.get(id=request.user.id)
            )

            try:
                watchlist.delete()
                alert_message = "Item removed from the watchlist."

            except:
                # Auction not saved
                print(
                    f"Log -> Error deleting watchlist auction:{id_auction} and user:{request.user.id}")
                alert_message = "Watch list entry doesn't exist."

        return HttpResponseRedirect(reverse("auctions_item",
                                            args=[id_auction]))

    except Auctions.DoesNotExist:
        # If not display an error message
        message = "This Auction Does Not Exist. Operation Cancelled."
        return render(request, "auctions/auctionsItem.html", {
            "message": message
        })
