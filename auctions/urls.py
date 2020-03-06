from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("auction/<int:id_auction>", views.auctions_item, name="auctions_item"),
    path("auctionAdd", views.auctions_add, name="auctions_add"),
    path("auctionBid", views.auctions_bid, name="auctions_bid"),
    path("auctionOper/<str:oper>/<int:id_auction>/",
         views.auctions_oper, name="auctions_oper"),
    path("auctionComment/",
         views.auctions_comment, name="auctions_comment"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories")
]
