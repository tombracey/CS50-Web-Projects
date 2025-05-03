from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import *


def listing(request, id):
    listing = Listing.objects.get(id=id)
    comments = listing.comments.all()
    user = request.user
    in_watchlist = user.is_authenticated and listing.watchlist.filter(id=user.id).exists()
    
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": comments,
        "in_watchlist": in_watchlist
    })


def remove_from_watchlist(request, id):
    listing = Listing.objects.get(id=id)
    user = request.user
    listing.watchlist.remove(user)
    return HttpResponseRedirect(reverse("listing",args=(id, )))

def add_to_watchlist(request, id):
    listing = Listing.objects.get(id=id)
    user = request.user
    listing.watchlist.add(user)
    return HttpResponseRedirect(reverse("listing",args=(id, )))

def watchlist(request):
    user = request.user
    listings = user.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })

def index(request):
    listings = Listing.objects.filter(active_status=True)
    categories = Category.objects.all()
    return render(request, "auctions/index.html", {
        "listings": listings,
        "categories": categories
    })

def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {"categories": categories})

def category_listings(request, category_name):
    category = Category.objects.get(name=category_name)
    listings = Listing.objects.filter(active_status=True, category=category)
    return render(request, "auctions/index.html", {
        "listings": listings,
        "categories": Category.objects.all()
    })

def show_categories(request):
    if request.method == "POST":
        category_name = request.POST.get('category')
        category_instance = Category.objects.get(name=category_name)
        listings = Listing.objects.filter(active_status=True, category=category_instance)
        categories = Category.objects.all()

        return render(request, "auctions/index.html", {
            "listings": listings,
            "categories": categories
        })
    
def comment(request, id):
    if request.method == "POST":
        user = request.user
        listing = Listing.objects.get(id=id)
        message = request.POST['comment']
        
        new_comment = Comment(user=user, listing=listing, message=message)
        new_comment.save()

    return HttpResponseRedirect(reverse("listing", args=(id,)))

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

def create_listing(request):
    if request.method == "GET":
        categories = Category.objects.all()
        return render(request, "auctions/create_listing.html", {
            "categories": categories
        })
    
    if request.method == "POST":
        user = request.user
        title = request.POST["title"]
        description = request.POST["description"]
        image_url = request.POST["image_url"]
        price = float(request.POST["price"])

        category = request.POST["category"]
        category_instance = Category.objects.get(name=category)

        new_listing = Listing(
            owner=user,
            name=title,
            description=description,
            image_url=image_url,
            price=price,  # Just a number
            category=category_instance
        )
        new_listing.save()

        return HttpResponseRedirect(reverse("index"))

def bid(request, id):
    if request.method == "POST":
        listing = Listing.objects.get(id=id)
        user = request.user
        bid_amount = float(request.POST["bid"])

        if bid_amount > listing.price:
            new_bid = Bid(user=user, bid=bid_amount, listing=listing)
            new_bid.save()

            listing.price = bid_amount
            listing.save()
        else:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "comments": listing.comments.all(),
                "in_watchlist": user.is_authenticated and listing.watchlist.filter(id=user.id).exists(),
                "error": "Your bid must exceed the current price"
            })

    return HttpResponseRedirect(reverse("listing", args=(id,)))


def close_auction(request, id):
    listing = Listing.objects.get(id=id)

    if request.user != listing.owner:
        return HttpResponse("You do not have permission to close this auction.", status=403)

    highest_bid = Bid.objects.filter(listing=listing).order_by('-bid').first()
    if highest_bid:
        listing.winner = highest_bid.user  

    listing.active_status = False
    listing.save()

    return HttpResponseRedirect(reverse("listing", args=[id]))
