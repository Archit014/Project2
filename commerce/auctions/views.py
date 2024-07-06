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
    return render(request, "auctions/index.html")


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

            f = Listings(item=name, description=description, start_bid=bid, image=image, status=True, seller=user)
            f.save()
    return render(request, "auctions/new.html",{
        "form": NewListingForm()
    })