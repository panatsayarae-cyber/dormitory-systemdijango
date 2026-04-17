from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, Bill, Tenant


def home(request):
    return render(request, 'home.html')


# ✅ LOGIN FIX
def login_view(request):
    if request.method == 'POST':
        id_card = request.POST.get('id_card')

        try:
            tenant = Tenant.objects.get(id_card=id_card)

            # 🔥 บันทึก session
            request.session['tenant_id'] = tenant.id

            return redirect('/dashboard/')

        except Tenant.DoesNotExist:
            return render(request, 'login.html', {
                'error': 'ไม่พบเลขบัตรนี้ในระบบ'
            })

    return render(request, 'login.html')


# ✅ LOGOUT
def logout_view(request):
    request.session.flush()
    return redirect('/')


# ✅ DASHBOARD (กันเข้าตรง)
def dashboard(request):
    if 'tenant_id' not in request.session:
        return redirect('/login/')

    tenant = Tenant.objects.get(id=request.session['tenant_id'])

    return render(request, 'dashboard.html', {
        'tenant': tenant
    })


# ✅ BILLS (เอาของตัวเองเท่านั้น)
def bills(request):
    if 'tenant_id' not in request.session:
        return redirect('/login/')

    tenant_id = request.session['tenant_id']
    bills = Bill.objects.filter(tenant_id=tenant_id).order_by('-id')

    return render(request, 'bills.html', {'bills': bills})


def repair(request):
    return render(request, 'repair.html')


def rooms(request):
    rooms = Room.objects.all().order_by('room_number')
    return render(request, 'rooms.html', {'rooms': rooms})


def room_detail(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    return render(request, 'rooms.html', {'room': room})