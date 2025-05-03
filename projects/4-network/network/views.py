from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.paginator import Paginator
import json

from .models import *


def index(request):
    all_posts = Post.objects.all()

    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    user_likes = []
    if request.user.is_authenticated:
        user_likes = Like.objects.filter(user_liking=request.user).values_list("post_liked_id", flat=True)

    return render(request, "network/index.html", {
        "page": page,
        "user_likes": list(user_likes)
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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

def post(request):
    if request.method=="POST":
        content = request.POST['content']
        user = User.objects.get(pk=request.user.id)
        post = Post(content=content, user=user)
        post.save()
        return HttpResponseRedirect(reverse(index))

def profile(request, id):
    user = User.objects.get(id=id)
    user_posts = Post.objects.filter(user=user).order_by("-created_at")

    paginator = Paginator(user_posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    followers = Follow.objects.filter(followee=user)
    following = Follow.objects.filter(follower=user)

    following_status = False
    if request.user.is_authenticated:
        following_status = Follow.objects.filter(follower=request.user, followee=user).exists()

    return render(request, "network/profile.html", {
        "username": user.username,
        "page": page,
        "followers": followers,
        "following": following,
        "following_status": following_status,
        "user": user
    })


def follow(request, id):
    user_to_follow = User.objects.get(id=id)
    Follow.objects.create(follower=request.user, followee=user_to_follow)
    return redirect('profile', id=id)

def unfollow(request, id):
    user_to_unfollow = User.objects.get(id=id)
    Follow.objects.filter(follower=request.user, followee=user_to_unfollow).delete()
    return redirect('profile', id=id)

def following(request):
    following = Follow.objects.filter(follower=request.user).values_list('followee', flat=True)
    all_posts = Post.objects.filter(user__in=following)

    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "page": page
    })

def edit_post(request, id):
    if request.method == "POST":
        post = Post.objects.get(id=id)
        if request.user != post.user:
            return JsonResponse({"error": "Unauthorised"}, status=403)
        data = json.loads(request.body)
        post.content = data["content"]
        post.save()
        return JsonResponse({"message": "Change successful", "content": data["content"]})

def change_like(request, id):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        post = Post.objects.get(id=id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found"}, status=404)

    like, created = Like.objects.get_or_create(user_liking=request.user, post_liked=post)

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    like_count = post.post_liked.count()

    return JsonResponse({
        "like_count": like_count,
        "liked": liked
    })