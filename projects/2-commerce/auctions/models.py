from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Listing(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=350)
    price = models.FloatField(default=0)
    starting_price = models.FloatField(default=0)
    image_url = models.CharField(max_length=350)
    active_status = models.BooleanField(default=True)
    category = models.ForeignKey(Category, models.CASCADE, blank=True, null=True, related_name="listings")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    watchlist = models.ManyToManyField(User, blank=True, related_name="watchlist")
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="won_auctions")

    def __str__(self):
        return self.name
    
class Bid(models.Model):
    bid = models.FloatField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f"{self.user.username} bid ${self.bid}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="user")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True, related_name="comments")
    message = models.CharField(max_length=250)

    def __str__(self):
        return f'{self.user} comment on {self.listing}'
    