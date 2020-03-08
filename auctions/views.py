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

menu is a parameter to activate the "bs nav pills" in the rigth menu item at layout.html

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
                menu = "cat"
            except:
                status = ""
                alert_message = "Category does not exist"
        else:
            # Category wasn´t informed so display active list
            auctions = Auctions.objects.filter(active=True)
            status = "Active"
            menu = "active"
    else:
        # Closed auctions only.
        auctions = Auctions.objects.filter(active=False)
        status = "Closed"
        menu = "close"

    alert_message = ""
    if len(auctions) == 0:
        alert_message = "There no items in the watchlist."

    return render(request, "auctions/index.html", {
        "auctions": auctions,
        "status": status,
        "alert_message": alert_message,
        # variable to activate the bs nav pills in the rigth menu
        "menu": menu
    })


"""
This view is invoked to displays user´s login form, and also process the post from the form to log-in.

Methods:
    GET : Displays the user´s login form.
    POST: Process the post submitted by the form. Login performed. 
    If ok redirect to index page, otherwise open the form again.
"""


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
                "message": "Invalid username and/or password.",
                "menu": "login"         # variable to activate the bs nav pills in the rigth menu
            })
    else:
        return render(request, "auctions/login.html", {
            "menu": "login"             # variable to activate the bs nav pills in the rigth menu
        })


"""
Performs the user logout.
"""


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


"""
This view is invoked to display the form which creates a new user and also process the post of the form.

Methods:
    GET : Displays the form to register a new user.
    POST: Process the post submitted by the form. User is created. Redirect to the index page.

"""


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match.",
                "menu": "new"
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken.",
                "menu": "new"          # variable to activate the bs nav pills in the rigth menu
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html", {
            "menu": "register"           # variable to activate the bs nav pills in the rigth menu
        })


"""
This view is invoked to display the page to create a new auction and also to process the post from the form.

Methods:
    GET : Displays the form to register a new auction.
    POST: Process the post submitted by the form. Auction is saved. Redirect to the auction item page.

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

        return HttpResponseRedirect(reverse("auctions_item",
                                            args=[auction.id_auction]))
    else:
        return render(request, "auctions/auctionsAdd.html", {
            "categories": Category.objects.all(),
            "menu": "new"
        })


"""
This view displays the auction item.

There are some redirects to this page, as this page displays the details of the auction.

Bear in mind that any redirect, can pass the alert message to be displayed as session variable.

Input:
    id_auction : Id of the auction to be displayed, it´s passed as URL parameter.

"""


def auctions_item(request, id_auction):

    # Initialize local variables.
    winner = False
    category_name = ""

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
        cat = Category.objects.get(auctions__id_auction=id_auction)
        category_name = cat.name

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
        "category": category_name,
        "watchlist": watchlist,
        "auction_owner": owner,
        "alert_message": alert_message,
        "higher_bid_message": higher_bid_message,
        "isTheWinner": winner
    })


"""
View used to save the bid, after saving the bid, this view redirects to auctions_item page. 
Notice a session variable is used to pass the alert_message to be displayed at the auctions_item page.

"""


def auctions_bid(request):

    if request.method == "POST":

        id_auction = request.POST["id_auction"]
        # return the higher bid for the auction.
        max_bid = maxBid(id_auction)
        if max_bid is None:
            max_bid = 0
        amount = float(request.POST["amount"])
        start_bid = Auctions.objects.get(id_auction=id_auction).start_bid

        # Bid placed is higher than highest bid and higher than Auction's start bid
        if amount > max_bid and amount > start_bid:
            try:
                # Save the bid
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
            # The amount placed was lower than required.

            if max_bid != 0 and amount < max_bid:
                # Already exist bids and the one placed was lower than the higher one
                request.session[
                    'alert_message'] = f"Bid Rejected. The bid of {amount} is lower than the higher one { max_bid}."
            else:
                # Bid placed was lower than the start bid
                request.session[
                    'alert_message'] = f"Bid Rejected. The bid of {amount} is lower than the initial bid of { start_bid }."

    # regardless the request method, displays the auction item page again,
    # alert message is passed as session variable.
    return HttpResponseRedirect(reverse("auctions_item",
                                        args=[id_auction]))


"""
Performs 3 operations over the auction displayed on the page. 
Operations are : Add to the logged user´s watchlist, Delete from logged user´s watchlist, Close the auction
After operation is performed, the response is redirected to the auction_item page.

Input
    oper : Operation to be performed (Add or Delete or Close). Passed as URL parameter.
    id_auction : Id of the auction. Passed as URL parameter.

"""


def auctions_oper(request, oper, id_auction):

    # Check if the auction exist.
    try:
        auction = Auctions.objects.get(id_auction=id_auction)
        request.session['alert_message'] = ""

        if oper == "Add":
            # Add to the watchlist.
            watchlist = Watchlist(
                id_auction=Auctions.objects.get(id_auction=id_auction),
                id_user=User.objects.get(id=request.user.id)
            )

            # Try to save the auction to the user´s watchlist.
            try:
                watchlist.save()
                request.session['alert_message'] = "Item added to the watchlist."

            except:
                # Auction not saved
                print(
                    f"Log -> Error adding watchlist: {id_auction} and user:{request.user.id}")
                request.session['alert_message'] = "Watch list item duplicated."

        elif oper == "Delete":
            # Delete auction from to the user´s watchlist.
            watchlist = Watchlist.objects.get(
                id_auction=Auctions.objects.get(id_auction=id_auction),
                id_user=User.objects.get(id=request.user.id)
            )

            # Try to delete the auction from the user´s watchlist
            try:
                watchlist.delete()
                request.session['alert_message'] = "Item removed from the watchlist."

            except:
                # Auction not saved
                print(
                    f"Log -> Error deleting watchlist auction:{id_auction} and user:{request.user.id}")
                request.session['alert_message'] = "Watchlist entry doesn't exist."

        elif oper == "Close":
            # Close the auction.

            # Returns the auction record, if the logged user isn´t the owner, the queryset will return
            # empty, so the try below wil raise an exception, otherwise aution will be closed.
            auction = Auctions.objects.get(
                id_auction=id_auction,
                id_user=request.user.id
            )

            # Try to close the auction.
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


"""
Saves the user´s comment

Method 
    POST : Saves the user´s comment, redirect again to the same page auctions_item.

"""


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


"""
Displays the user´s watchlist page.
The watchlist elements are stored in a list of objects. This list is used by the template.
This approach was required to get the data from the auction to be displayed.
I don´t know yet how to execute a database query using Django, when joining 2 or more table.

Method 
    GET : Returns the watchlist page rendered.

"""


def watchlist(request):

    # Class used to the watchlist object
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
    id_user = request.user.id                       # get the user logged in.

    watch = []                                      # Initiate the list
    for auction in auctions:
        # loop over all auctions records.

        if IsWatchlist(auction.id_auction, id_user):
            # Auction is in the user´s watchlist

            maxbid = maxBid(auction.id_auction)     # Get the higher bid.

            # initiate the object
            w = Watch(int(auction.id_auction), auction.title,
                      auction.start_bid,
                      maxbid)
            # add to the list
            watch.append(w)

    alert_message = ""
    if len(watch) == 0:
        alert_message = "There no items in the watchlist."

    return render(request, "auctions/watchlist.html", {
        "watchlist": watch,
        "alert_message": alert_message,
        "menu": "watch"             # variable to activate the bs nav pills in the rigth menu
    })


"""
Displays the category list page.

Method 
    GET : Returns the category page rendered.

"""


def categories(request):

    categories = Category.objects.all()

    alert_message = ""
    if len(categories) == 0:
        alert_message = "There no registered categories."

    return render(request, "auctions/categories.html", {
        "categories": categories,
        "alert_message": alert_message,
        "menu": "cat"               # variable to activate the bs nav pills in the rigth menu
    })
