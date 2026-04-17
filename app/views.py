from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, Bill, Tenant, Maintenance, Contract


def home(request):
    return render(request, 'home.html')


# ================= LOGIN =================
def login_view(request):
    if request.method == 'POST':
        id_card = request.POST.get('id_card')

        try:
            tenant = Tenant.objects.get(id_card=id_card)
            request.session['tenant_id'] = tenant.id
            return redirect('/dashboard/')
        except Tenant.DoesNotExist:
            return render(request, 'login.html', {'error': 'ไม่พบผู้ใช้งาน'})

    return render(request, 'login.html')


# ================= LOGOUT =================
def logout_view(request):
    request.session.flush()
    return redirect('/')


# ================= DASHBOARD =================
def dashboard(request):
    tenant_id = request.session.get('tenant_id')

    if not tenant_id:
        return redirect('/login/')

    tenant = Tenant.objects.get(id=tenant_id)

    # ✅ ใช้ contract แทน
    contract = Contract.objects.filter(tenant=tenant).first()

    room = contract.room if contract else None

    bill = Bill.objects.filter(contract__tenant=tenant).order_by('-id').first()

    return render(request, 'dashboard.html', {
        'tenant': tenant,
        'room': room,
        'bill': bill
    })


# ================= BILLS =================
def bills(request):
    tenant_id = request.session.get('tenant_id')

    if not tenant_id:
        return redirect('/login/')

    tenant = Tenant.objects.get(id=tenant_id)

    # ✅ FIX ตรงนี้
    bills = Bill.objects.filter(contract__tenant=tenant).order_by('-id')

    return render(request, 'bills.html', {'bills': bills})


# ================= REPAIR =================
def repair(request):
    tenant_id = request.session.get('tenant_id')

    if not tenant_id:
        return redirect('/login/')

    tenant = Tenant.objects.get(id=tenant_id)

    contract = Contract.objects.filter(tenant=tenant).first()
    room = contract.room if contract else None

    if request.method == 'POST':
        detail = request.POST.get('detail')
        image = request.FILES.get('image')

        Maintenance.objects.create(
            tenant=tenant,
            room=room,
            detail=detail,
            image=image,
            status='รอดำเนินการ'
        )

        return redirect('/repair/')

    repairs = Maintenance.objects.filter(tenant=tenant).order_by('-id')

    return render(request, 'repair.html', {
        'room': room,
        'repairs': repairs
    })