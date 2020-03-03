from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("auctionAdd", views.auctions_add, name="auctions_add"),
    path("auction/<int:id_auction>", views.auctions_item, name="auctions_item"),
    path("auctionBid", views.auctions_bid, name="auctions_bid"),
    path("auctionWatchlist/<str:oper>/<int:id_auction>/",
         views.auctions_oper, name="auctions_watchlist"),
    path("auctionClose", views.auctions_close, name="auctions_close")

]
