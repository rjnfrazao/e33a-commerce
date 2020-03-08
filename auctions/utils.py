from .models import Bid, Watchlist
from django.db.models import Max


"""
    Function returns the higher bid from an auction.
    In case there are no bid returns 0
"""


def maxBid(id_auction):
    try:
        # Filter all bids from the auction
        search_max = Bid.objects.filter(id_auction=id_auction)

        if search_max.exists():
            # Get the higher amount
            max_amount = search_max.aggregate(
                Max('amount'))
            return max_amount["amount__max"]
        else:
            # Query set is empty. No bids yet, so returns 0.
            return 0
    except:
        return 0


"""
    Function returns True in case the auctions is in the watchlist of the user, otherwise returns false.

    input
    id_auction : Auction id
    id_user : User if
"""


def IsWatchlist(id_auction, id_user):

    try:
        # Filter all bids from the auction
        # print(f"isWatchlist -> auction: {id_auction}, user:{id_user}")
        isThere = Watchlist.objects.filter(
            id_auction=id_auction, id_user=id_user).exists()

        return isThere
    except:
        return False


"""
    Function : Returns True if the user is the same of the higher bid, otherwise returns false.

    Input : 
    id_auction : get the lis of bids from this auction
    user : user to be checked (should be the logged user)
"""


def isWinner(id_auction, user):

    try:
        # Filter all bids from the auction
        bid = Bid.objects.filter(id_auction=id_auction).order_by('-amount')

        # Check if exist bids for the auction
        if bid.exists():
            for b in bid:   # Force the loop to get the first record
                # Check if it´s the same user.
                if b.id_user == user:
                    return True
                break       # Exit. Just the first is needed.
        else:
            return False
    except:
        return False
