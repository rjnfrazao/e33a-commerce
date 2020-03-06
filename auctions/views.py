from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Auctions, Bid, Comments, Watchlist
from .utils import maxBid, IsWatchlist, isWinner

"""
Page displays the auctions listing, it displays three different conditions : Closed only, Active Only,
and Filtered by a category

The following parameters apply:
q=Closed : Display closed auctions.
c=<id_category> : Display the list of auctions which belongs to the informed category.
Otherwise : Display active auctions.
"""


def index(request):

    if request.GET.get("q") != "closed":
        # Closed auctions wasn't requested, so keep working on active only.

        if request.method == 'GET' and 'c' in request.GET:
            # Category was informed so filter the auctions per category.
            auctions = Auctions.objects.filter(
                id_category=request.GET.get("c"), active=True)
            try:
                print(request.GET.get("c"))
                category = Category.objects.get(
                    id_category=request.GET.get("c"))
                status = f"Category {category.name} "
            except:
                status = ""
                alert_message = "Category does not exist"
        else:
            # Category wasn´t informed so display active list
            auctions = Auctions.objects.filter(active=True)
            status = "Active"
    else:
        # Closed auctions only.
        auctions = Auctions.objects.filter(active=False)
        status = "Closed"

    alert_message = ""
    if len(auctions) == 0:
        alert_message = "There no items in the watchlist."

    return render(request, "auctions/index.html", {
        "auctions": auctions,
        "status": status,
        "alert_message": alert_message
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


"""
Page to register auctions.


"""


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
            active=True
        )
        auction.save()
        print("Saved Auction: ", auction.id_auction)
        return HttpResponseRedirect(reverse("auctions_item",
                                            args=[auction.id_auction]))
    else:
        return render(request, "auctions/auctionsAdd.html", {
            "categories": Category.objects.all()
        })


"""
Page displays the auction item.

There are some redirects to this page, as this page displays the details of the auction.

"""


def auctions_item(request, id_auction):

    # Initialize local variables.
    winner = False

    # It can be a redirect, so check if a alert message needs to be presented.
    try:
        alert_message = request.session["alert_message"]
        # Clear the session variable
        del request.session["alert_message"]
    except:
        alert_message = ""

    # check if id_auction exists
    try:
        auction = Auctions.objects.get(id_auction=id_auction)

        # Retrieve category name
        #cat = Category.objects.get(id_category=auction.id_category)
        #category_name = cat.name

        try:
            # Retrieve all comments from the auction.
            comments = Comments.objects.filter(id_auction=id_auction)
        except:
            # In case there are no comments keep it clear.
            comments = None

        try:
            # Get the higher bid for the auction.
            max_bid = maxBid(id_auction)

            if max_bid == 0:
                higher_bid_message = "<< NO BIDS YET >>"            # There are no bids yet
            else:
                # Higher bid was found.
                higher_bid_message = f" - Higher bid is {max_bid}"

            if not auction.active:
                # Check if current user is the winner of the bid
                if isWinner(id_auction, request.user):
                    alert_message = alert_message + \
                        "Congratulations. You are the WINNER of this bid."
                    winner = True
        except:
            # In case there are no comments keep it clear.
            winner = False

    except Auctions.DoesNotExist:
        # id_auction doesn't exist, display an error message
        return render(request, "auctions/auctionsItem.html", {
            "error_message": "This Auction Does Not Exist!"
        })

    # Here just because I can´t get the user id from the auction object.
    auctionUser = User.objects.get(username=auction.id_user)

    # Check if the auction is in the user´s watchlist.
    try:
        Watchlist.objects.get(id_auction=id_auction, id_user=request.user)
        watchlist = True
    except:
        watchlist = False

    # Check if the auction's user is the one which created the auction
    try:
        if auctionUser.id == request.user.id:
            owner = True
        else:
            owner = False
    except:
        # user is not logged.
        owner = False

    # return the page
    return render(request, "auctions/auctionsItem.html", {
        "auction": auction,
        "comments": comments,
        "user": auction.id_user,
        "category": auction.id_category,
        "watchlist": watchlist,
        "auction_owner": owner,
        "alert_message": alert_message,
        "higher_bid_message": higher_bid_message,
        "isTheWinner": winner
    })


def auctions_bid(request):

    if request.method == "POST":

        id_auction = request.POST["id_auction"]
        # return the higher bid for the auction.
        max_bid = maxBid(id_auction)
        if max_bid is None:
            max_bid = 0
        amount = float(request.POST["amount"])
        start_bid = Auctions.objects.get(id_auction=id_auction).start_bid

        print(f"start bid: {start_bid}, max bid: {max_bid}")
        # Bid placed is higher than highest bid and higher than Auction's start bid
        if amount > max_bid and amount > start_bid:
            try:
                print(f"{request.user.id}, {id_auction}, {amount}")
                bid = Bid(
                    id_user=request.user,
                    id_auction=Auctions.objects.get(id_auction=id_auction),
                    amount=amount,
                    active=True
                )
                bid.save()

                request.session['alert_message'] = f"Bid placed. Amount {amount} by user {request.user.username}."
            except:
                # Failed to save the new Bid
                request.session['alert_message'] = f"Bid Rejected. Save bid failed."
        else:
            if amount < start_bid:
                # Bid placed was lower than the start bid
                request.session[
                    'alert_message'] = f"Bid Rejected. The bid of {amount} is lower than the initial bid of { start_bid }."
            else:
                # Bid placed was lower than the higher one
                request.session[
                    'alert_message'] = f"Bid Rejected. The bid of {amount} is lower than the higher one { max_bid}."

        return HttpResponseRedirect(reverse("auctions_item",
                                            args=[id_auction]))

    else:
        # Http get redisplay the page again.
        return HttpResponseRedirect(reverse("auctions_item",
                                            args=[id_auction]))


"""
Perform 3 operations. Add watchlist, Delete watchlist, Close Auction

"""


def auctions_oper(request, oper, id_auction):

    # REMOVE FROM UTILS auction = utils.auctionExist(id_auction)

    # Check if the auction exist.
    try:
        auction = Auctions.objects.get(id_auction=id_auction)
        request.session['alert_message'] = ""

        if oper == "Add":

            watchlist = Watchlist(
                id_auction=Auctions.objects.get(id_auction=id_auction),
                id_user=User.objects.get(id=request.user.id)
            )

            try:
                watchlist.save()
                request.session['alert_message'] = "Item added to the watchlist."

            except:
                # Auction not saved
                print(
                    f"Log -> Error adding watchlist: {id_auction} and user:{request.user.id}")
                request.session['alert_message'] = "Watch list item duplicated."

        elif oper == "Delete":

            watchlist = Watchlist.objects.get(
                id_auction=Auctions.objects.get(id_auction=id_auction),
                id_user=User.objects.get(id=request.user.id)
            )

            try:
                watchlist.delete()
                request.session['alert_message'] = "Item removed from the watchlist."

            except:
                # Auction not saved
                print(
                    f"Log -> Error deleting watchlist auction:{id_auction} and user:{request.user.id}")
                request.session['alert_message'] = "Watchlist entry doesn't exist."

        elif oper == "Close":

            auction = Auctions.objects.get(
                id_auction=id_auction,
                id_user=request.user.id
            )
            try:
                auction.active = False
                auction.save()
                request.session['alert_message'] = "Auction was closed."
            except:
                # Auction not closed
                print(
                    f"Log -> Error closing the  auction:{id_auction} from user:{request.user.id},")
                request.session['alert_message'] = "Auction can't be closed. You must be the auction´s owner."

        return HttpResponseRedirect(reverse("auctions_item",
                                            args=[id_auction]))

    except Auctions.DoesNotExist:
        # If not display an error message
        error_message = "This Auction Does Not Exist. Operation Cancelled."
        return render(request, "auctions/auctionsItem.html", {
            "error_message": error_message
        })


def auctions_comment(request):

    if request.method == "POST":

        id_auction = request.POST["id_auction"]
        comment = Comments(
            id_user=request.user,
            id_auction=Auctions.objects.get(id_auction=id_auction),
            comment=request.POST["comment"]
        )
        comment.save()

        return HttpResponseRedirect(reverse("auctions_item",
                                            args=[id_auction]))


def watchlist(request):

    class Watch:
        id_auction = 0
        title = ""
        start_bid = 0
        higher_bid = 0

        def __init__(self, id_auction, title, start, higher):
            # Instance Variable
            self.id_auction = id_auction
            self.title = title
            self.start_bid = start
            self.higher = higher

    auctions = Auctions.objects.filter(active=True)
    id_user = request.user.id

    watch = []
    for auction in auctions:

        if IsWatchlist(auction.id_auction, id_user):
            #print("id_auction:", auction.id_auction)
            maxbid = maxBid(auction.id_auction)
            w = Watch(int(auction.id_auction), auction.title,
                      auction.start_bid,
                      maxbid)
            watch.append(w)

    alert_message = ""
    if len(watch) == 0:
        alert_message = "There no items in the watchlist."

    return render(request, "auctions/watchlist.html", {
        "watchlist": watch,
        "alert_message": alert_message
    })


def categories(request):

    categories = Category.objects.all()

    alert_message = ""
    if len(categories) == 0:
        alert_message = "There no items in the watchlist."

    return render(request, "auctions/categories.html", {
        "categories": categories,
        "alert_message": alert_message
    })
