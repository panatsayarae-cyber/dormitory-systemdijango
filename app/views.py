from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, Bill, Tenant


def home(request):
    return render(request, 'home.html')


def login_view(request):
    return render(request, 'login.html')


def logout_view(request):
    request.session.flush()
    return redirect('/')


def dashboard(request):
    return render(request, 'dashboard.html')


def bills(request):
    bills = Bill.objects.all().order_by('-id')
    return render(request, 'bills.html', {'bills': bills})


def repair(request):
    return render(request, 'repair.html')


def rooms(request):
    rooms = Room.objects.all().order_by('room_number')
    return render(request, 'rooms.html', {'rooms': rooms})


def room_detail(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    return render(request, 'rooms.html', {'room': room})