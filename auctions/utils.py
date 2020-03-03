from .models import Auctions


def auctionExist(id_auction):

    # Check if the auction exist.
    try:
        auction = Auctions.objects.get(id_auction=id_auction)
        return auction
    except Auctions.DoesNotExist:
        # If not display an error message
        return False
