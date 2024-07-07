from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms



from .models import User,Listings,Bid,Comment,CATEGORY_CHOICES


class NewListingForm(forms.Form):
    name = forms.CharField(label="Item name", max_length=64, widget=forms.TextInput(attrs={
        'autocomplete':'off'
    }))
    description = forms.CharField(label="Item Description",widget=forms.Textarea)
    image = forms.URLField(label="Image URL (optional)", required=False)
    category = forms.ChoiceField(label="Category", choices=CATEGORY_CHOICES)
    bid = forms.IntegerField(label="Minimum Bid", initial=0)

def index(request):
    listings = Listings.objects.filter(status = True)
    return render(request, "auctions/index.html",{
        "listings":listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def new(request):
    if request.method == "POST":
        form = NewListingForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data["name"]
            description = form.cleaned_data["description"]
            image = form.cleaned_data["image"]
            category = form.cleaned_data["category"]
            bid = form.cleaned_data["bid"]

            f = Listings(category = category, item=name, description=description, start_bid=bid, image=image, status=True, seller=user)
            f.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/new.html",{
                "form": form
            })
    return render(request, "auctions/new.html",{
        "form": NewListingForm()
    })

@login_required
def item(request, title):
    listing = Listings.objects.get(item = title)
    cmnt = Comment.objects.filter(item = listing)
    user = User.objects.get(username = request.user)
    if listing.current_bid != None:
        winner = listing.current_bid.user
    else:
        winner = request.user
    lists = user.item.all()
    is_watchlist = False
    is_active = listing.status
    for list in lists:
        if list.item == title:
            is_watchlist = True
            break
    
    if request.method == "POST":
        if listing.seller == request.user:
            listing.status = False
            listing.save()
            return HttpResponseRedirect(reverse("index"))
        
        watchlist = request.POST['watchlist']
        comment = request.POST['comment']
        bid = request.POST['bid']

        if is_watchlist:
            if watchlist == "true":
                if listing.seller != request.user:
                    for list in lists:
                        if list.item == title:
                            user.item.remove(list)
                else:
                    message = "You cannot remove watchlist from your own product"
                    return render(request, "auctions/error.html",{
                        "message":message
                    })
        else:
            if watchlist == "true":
                if listing.seller != request.user:
                    user.item.add(listing)
                else:
                    message = "You cannot add watchlist to your own product"
                    return render(request, "auctions/error.html",{
                        "message":message
                    })
        
        if comment:
            if listing.seller != request.user:
                f = Comment(user = request.user, item = listing, comment = comment)
                f.save()
            else:
                message = "You cannot add comments to your own product"
                return render(request, "auctions/error.html",{
                    "message":message
                })
        if bid:
            bid = int(bid)
            if listing.seller != request.user:
                if listing.current_bid != None:
                    if bid > listing.current_bid.bid:
                        f = Bid(user = request.user, item = listing, bid = bid)
                        f.save()
                        listing.current_bid = f
                        listing.save()
                    else :
                        message = "Bid should be higher than current bid"
                        return render(request, "auctions/error.html",{
                            "message":message
                        })
                else:
                    if bid > listing.start_bid:
                        f = Bid(user = request.user, item = listing, bid = bid)
                        f.save()
                        listing.current_bid = f
                        listing.save()
            else:
                message = "You cannot bid to your own product"
                return render(request, "auctions/error.html",{
                    "message":message
                })
        return render(request, "auctions/item.html",{
            "listing":listing,
            "user":request.user,
            "comments":cmnt,
            "is_watchlist":is_watchlist,
            "is_active":is_active,
            "winner":winner
        })


    return render(request, "auctions/item.html",{
        "listing":listing,
        "user":request.user,
        "comments":cmnt,
        "is_watchlist":is_watchlist,
        "is_active":is_active,
        "winner":winner
    })

@login_required
def watchlist(request):
    user = User.objects.get(username = request.user)
    lists = user.item.all()
    return render(request, "auctions/watchlist.html",{
        "lists":lists
    })

@login_required
def categories(request):
    return render(request, "auctions/categories.html",{
        "categories":CATEGORY_CHOICES
    })

@login_required
def list(request,category):
    listings = Listings.objects.filter(category = category, status = True)
    return render(request, "auctions/list.html",{
        "listings":listings
    })

@login_required
def closed(request):
    listings = Listings.objects.filter(status = False)
    return render(request, "auctions/closed.html",{
        "listings":listings
    })