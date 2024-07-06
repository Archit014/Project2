from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    first = models.CharField(max_length=64,blank=True)
    last = models.CharField(max_length=64, blank=True)
    item = models.ManyToManyField("Listings", blank=True, related_name="watchlist")

CATEGORY_CHOICES = [
    ('FN', 'Fashion'),
    ('TS', 'Toys'),
    ('ES', 'Electronics'),
    ('HE', 'Home'),
]
class Listings(models.Model):
    category = models.CharField(
        max_length=2,
        choices=CATEGORY_CHOICES,
    )
    item = models.CharField(max_length=64)
    description = models.TextField()
    start_bid = models.IntegerField(default=0)
    image = models.URLField()
    status = models.BooleanField(default=True)
    current_bid = models.ForeignKey("Bid", models.SET_NULL, blank=True, null =True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listing")

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bid")
    item = models.ForeignKey(Listings, on_delete=models.CASCADE)
    bid = models.IntegerField()

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment")
    item = models.ForeignKey(Listings, on_delete=models.CASCADE)
    comment = models.TextField()