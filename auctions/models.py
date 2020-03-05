from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    pass


class Category(models.Model):
    id_category = models.CharField(max_length=5, primary_key=True)
    name = models.CharField(max_length=50)


class Auctions(models.Model):
    id_auction = models.AutoField(primary_key=True)
    id_category = models.ForeignKey(
        Category, to_field='id_category', on_delete=models.PROTECT, db_column='id_category')
    id_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        to_field='id',
        on_delete=models.CASCADE,
        null=True,
        db_column='id_user'
    )
    title = models.CharField("Title", max_length=100)
    description = models.TextField("Description")
    start_bid = models.FloatField("Start Bid", null=False)
    image_url = models.CharField("Image URL", max_length=255, null=True)
    date_creation = models.DateTimeField(auto_now=True)
    active = models.BooleanField("Active", default="True")

    def __str__(self):
        return f"id = {self.id_auction}, Title = {self.title}, User = {self.id_user}, Start bid = {self.start_bid}, Active = {self.active}"


class Bid(models.Model):
    id_bid = models.AutoField(primary_key=True)
    id_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        to_field='id',
        on_delete=models.CASCADE,
        db_column='id_user'
    )
    id_auction = models.ForeignKey(
        Auctions, to_field='id_auction', on_delete=models.PROTECT, db_column='id_auction')
    amount = models.FloatField("Amount")
    active = models.BooleanField("Active", default="True")

    def __str__(self):
        return f"id bid = {self.id_bid}, id user = {self.id_user}, id_auction = {self.id_auction}, Amount = {self.amount}, Active = {self.active}"


class Comments(models.Model):
    id_comment = models.AutoField(primary_key=True)
    id_auction = models.ForeignKey(
        Auctions, to_field='id_auction', on_delete=models.CASCADE, db_column='id_auction')
    id_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        to_field='id',
        on_delete=models.CASCADE,
        db_column='id_user'
    )
    comment = models.CharField("Comment", max_length=255)


class Watchlist(models.Model):
    id_auction = models.ForeignKey(
        Auctions, to_field='id_auction', on_delete=models.CASCADE, db_column='id_auction')
    id_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        to_field='id',
        on_delete=models.CASCADE,
        db_column='id_user')

    class Meta:
        unique_together = ("id_auction", "id_user")
