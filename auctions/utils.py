from .models import Bid
from django.db.models import Max


"""
    Function returns the higher bid from an auction.
    In case there are no bid returns 0
"""


def maxBid(id_auction):
    try:
        # Filter all bids from the auction
        search_max = Bid.objects.filter(id_auction=id_auction)

        # Get the higher amount
        max_amount = search_max.aggregate(
            Max('amount'))

        return max_amount["amount__max"]
    except e:
        return 0
