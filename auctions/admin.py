from django.contrib import admin
from .models import User, Category, Auctions, Bid, Comments, Watchlist

# Register your models here.
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Auctions)
admin.site.register(Bid)
admin.site.register(Comments)
admin.site.register(Watchlist)
