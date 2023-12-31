from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm
import http.client
import json
import jwt
import random
import math

# Create y3our views here.

# rooms = [
#     {'id': 1, 'name': 'Lets learn python!'},
#     {'id': 2, 'name': 'Design with me'},
#     {'id': 3, 'name': 'Frontend developers'},
# ]


def jwt_login_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        token = request.COOKIES.get('access_token')
        if token:
            try:
                decoded_token = jwt.decode(
                    token, 'nexuschat', algorithms=["HS256"])
                return view_func(request, *args, **kwargs)
            except jwt.ExpiredSignatureError:
                pass
            except jwt.InvalidTokenError:
                pass
        return redirect('login')
    return login_required(_wrapped_view)


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            encoded_jwt = jwt.encode(
                {"email": user.email}, "nexuschat", algorithm="HS256")
            response = HttpResponseRedirect("/")
            print("Sending response")
            response.set_cookie("access_token", encoded_jwt)
            return response
        else:
            messages.error(request, 'Username OR password does not exit')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            encoded_jwt = jwt.encode(
                {"email": user.email}, "nexuschat", algorithm="HS256")

            user.save()
            login(request, user)
            response = HttpResponse()
            response.set_cookie("access_token", encoded_jwt)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')

    return render(request, 'base/login_register.html', {'form': form})


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )

    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q))[0:3]

    context = {'rooms': rooms, 'topics': topics,
               'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages,
               'participants': participants}
    return render(request, 'base/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms,
               'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def joinRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user in room.participants.all():
        return HttpResponse('You are already a participant of this room!')

    room.participants.add(request.user)
    return redirect('room', pk=room.id)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(request, 'base/update-user.html', {'form': form})


@login_required(login_url='login')
def extAPICall(request):
    # conn = http.client.HTTPSConnection("shazam.p.rapidapi.com")

    # headers = {
    #     'X-RapidAPI-Key': "4449fd3e75mshafba1df15a7e228p1ba074jsneaf6ef580dda",
    #     'X-RapidAPI-Host': "shazam.p.rapidapi.com"
    # }

    # conn.request(
    #     "GET", "/songs/list-recommendations?key=484129036&locale=en-US", headers=headers)

    # res = conn.getresponse()
    # data = res.read()

    # bloomberg api call - get stats for stock

    conn1 = http.client.HTTPSConnection(
        "bloomberg-market-and-financial-news.p.rapidapi.com")

    headers1 = {
        'X-RapidAPI-Key': "4449fd3e75mshafba1df15a7e228p1ba074jsneaf6ef580dda",
        'X-RapidAPI-Host': "bloomberg-market-and-financial-news.p.rapidapi.com"
    }

    conn1.request(
        "GET", "/stock/get-statistics?id=aapl%3Aus&template=STOCK", headers=headers1)

    res1 = conn1.getresponse()
    data1 = res1.read()

    # yh news - get popular watchlist for market

    conn2 = http.client.HTTPSConnection("yh-finance.p.rapidapi.com")

    headers2 = {
        'X-RapidAPI-Key': "4449fd3e75mshafba1df15a7e228p1ba074jsneaf6ef580dda",
        'X-RapidAPI-Host': "yh-finance.p.rapidapi.com"
    }

    conn2.request(
        "GET", "/market/get-earnings?region=US&startDate=1585155600000&endDate=1589475600000&size=10", headers=headers2)

    res2 = conn2.getresponse()
    data2 = res2.read()

    return render(request, 'base/extApiCall.html', {'data1': json.loads(data1.decode(
        "utf-8")), 'data2': json.loads(data2.decode(
            "utf-8"))})


@login_required(login_url='login')
def mathFacts(request):
    return render(request, 'base/mathFacts.html')


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics})


def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages': room_messages})


@login_required(login_url='login')
def videoCall(request, pk):
    return render(request, 'base/vc-lobby.html', {'roomId': pk, 'user': request.user.username})


@login_required(login_url='login')
def streamCall(request, pk):
    uid = str(math.floor(random.random() * 10000))
    return render(request, 'base/vc-room.html', {'name': request.GET.get('name'), 'vcRoom': request.GET.get('room'), 'user': request.user, 'room': Room.objects.get(id=pk), 'uid': uid})
