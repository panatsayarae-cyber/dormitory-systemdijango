from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, Bill, Tenant, Maintenance


# ================== หน้าแรก ==================
def home(request):
    return render(request, 'home.html')


# ================== LOGIN ==================
def login_view(request):
    if request.method == "POST":
        id_card = request.POST.get("id_card")

        try:
            tenant = Tenant.objects.get(id_card=id_card)
            request.session['tenant_id'] = tenant.id
            return redirect('/dashboard/')
        except Tenant.DoesNotExist:
            return render(request, 'login.html', {'error': 'ไม่พบผู้ใช้'})

    return render(request, 'login.html')


# ================== LOGOUT ==================
def logout_view(request):
    request.session.flush()
    return redirect('/')


# ================== DASHBOARD ==================
def dashboard(request):
    tenant_id = request.session.get('tenant_id')

    if not tenant_id:
        return redirect('/login/')

    tenant = Tenant.objects.get(id=tenant_id)
    contract = tenant.contract_set.first()

    bill = Bill.objects.filter(contract=contract).order_by('-id').first()

    return render(request, 'dashboard.html', {
        'tenant': tenant,
        'bill': bill,
        'room': contract.room if contract else None
    })


# ================== ดูบิล ==================
def bills(request):
    tenant_id = request.session.get('tenant_id')

    if not tenant_id:
        return redirect('/login/')

    try:
        tenant = Tenant.objects.get(id=tenant_id)
        contract = tenant.contract_set.first()   # ดึงสัญญา
        bills = Bill.objects.filter(contract=contract).order_by('-id')
    except:
        bills = []

    return render(request, 'bills.html', {'bills': bills})

# ================== แจ้งซ่อม ==================
def repair(request):
    tenant_id = request.session.get('tenant_id')

    if not tenant_id:
        return redirect('/login/')

    tenant = Tenant.objects.get(id=tenant_id)
    contract = tenant.contract_set.first()

    if request.method == "POST":
        detail = request.POST.get("detail")

        Maintenance.objects.create(
            tenant=tenant,
            room=contract.room,   # ✅ ใช้ผ่าน contract
            detail=detail,
            status="รอดำเนินการ"
        )

        return redirect('/dashboard/')

    return render(request, 'repair.html')


# ================== ห้อง ==================
def rooms(request):
    rooms = Room.objects.all().order_by('room_number')
    return render(request, 'rooms.html', {'rooms': rooms})


def room_detail(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    return render(request, 'rooms.html', {'room': room})