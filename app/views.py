from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, Bill


# ================== 🔥 หน้าแรก ==================
def home(request):
    return render(request, 'home.html')


# ================== 🔐 Login ==================
def login_view(request):
    return render(request, 'login.html')


# ================== 🔓 Logout ==================
def logout_view(request):
    return redirect('/')


# ================== 📊 Dashboard ==================
def dashboard(request):
    return render(request, 'dashboard.html')


# ================== 💸 Bills ==================
def bills(request):
    bills = Bill.objects.all().order_by('-id')
    return render(request, 'bills.html', {
        'bills': bills
    })


# ================== 🔧 Repair ==================
def repair(request):
    return render(request, 'repair.html')


# ================== 🏢 Rooms ==================
def rooms(request):
    rooms = Room.objects.all().order_by('room_number')
    return render(request, 'rooms.html', {
        'rooms': rooms
    })


# ================== 🔍 Room Detail ==================
def room_detail(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    return render(request, 'rooms.html', {
        'room': room
    })