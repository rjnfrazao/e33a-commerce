from .models import Bid


"""
    Function returns the higher bid from an auction.
    In case there are no bid returns 0
"""


def maxBid(id_auction):
   # try:
    max = Bid.objects.filter(id_auction=id_auction)
    return max.aggregate(Max('amount'))
   # except e:
    return 0
