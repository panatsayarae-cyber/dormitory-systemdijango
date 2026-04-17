from django.shortcuts import render, redirect, get_object_or_404
from .models import Tenant, Contract, Bill, Maintenance, Room
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from io import BytesIO
import qrcode

# PDF
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# ================== TENANT CHECK ==================
def tenant_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('tenant_id'):
            return redirect('/login/')
        return view_func(request, *args, **kwargs)
    return wrapper


# ================== HOME (หน้าเลือก) ==================
def home(request):
    return render(request, 'home.html')


# ================== LOGIN ==================
def login_view(request):
    error = ""

    if request.method == 'POST':
        id_card = request.POST.get('id_card')

        try:
            tenant = Tenant.objects.get(id_card=id_card)
            request.session['tenant_id'] = tenant.id

            return redirect('/dashboard/')   # ✅ ไป dashboard

        except Tenant.DoesNotExist:
            error = "ไม่พบข้อมูลผู้เช่า"

    return render(request, 'login.html', {'error': error})


# ================== DASHBOARD ==================
@tenant_required
def dashboard(request):

    tenant = get_object_or_404(Tenant, id=request.session['tenant_id'])
    contract = Contract.objects.filter(tenant=tenant).first()
    bill = Bill.objects.filter(contract=contract).order_by('-id').first()

    return render(request, 'dashboard.html', {
        'tenant': tenant,
        'contract': contract,
        'bill': bill
    })


# ================== LOGOUT ==================
def logout_view(request):
    request.session.flush()
    return redirect('/')   # 🔥 กลับหน้า home


# ================== REPAIR ==================
@tenant_required
def repair(request):

    tenant = get_object_or_404(Tenant, id=request.session['tenant_id'])
    contract = Contract.objects.filter(tenant=tenant).first()

    if not contract:
        return redirect('/dashboard/')

    if request.method == "POST":
        detail = request.POST.get("detail")
        image = request.FILES.get("image")

        if detail:
            Maintenance.objects.create(
                tenant=tenant,
                room=contract.room,
                detail=detail,
                image=image if image else None
            )

        return redirect('/repair/')

    repairs = Maintenance.objects.filter(tenant=tenant).order_by('-id')

    return render(request, 'repair.html', {
        'repairs': repairs,
        'room': contract.room
    })


# ================== BILLS ==================
@tenant_required
def bills(request):

    tenant = get_object_or_404(Tenant, id=request.session['tenant_id'])
    bills = Bill.objects.filter(contract__tenant=tenant).order_by('-id')

    return render(request, 'bills.html', {
        'bills': bills
    })


# ================== UPLOAD SLIP ==================
@tenant_required
def upload_slip(request):

    if request.method == "POST":
        bill_id = request.POST.get("bill_id")
        slip = request.FILES.get("slip")

        bill = get_object_or_404(Bill, id=bill_id)

        if slip:
            bill.slip = slip
            bill.save()

    return redirect('/bills/')


# ================== ADMIN CHECK ==================
def admin_only(user):
    return user.is_staff


# ================== ROOMS ==================
@login_required
@user_passes_test(admin_only)
def rooms(request):

    toggle_id = request.GET.get('toggle')
    if toggle_id:
        room = get_object_or_404(Room, id=toggle_id)
        room.status = 'ไม่ว่าง' if room.status == 'ว่าง' else 'ว่าง'
        room.save()
        return redirect('/rooms/')

    rooms = Room.objects.all().order_by('room_number')

    floor_data = {}

    for room in rooms:
        floor = room.room_number[0]

        contract = Contract.objects.filter(room=room).first()
        tenant = contract.tenant if contract else None

        room_data = {
            'room': room,
            'tenant': tenant,
            'contract': contract
        }

        if floor not in floor_data:
            floor_data[floor] = []

        floor_data[floor].append(room_data)

    return render(request, 'rooms.html', {
        'floor_data': floor_data
    })


# ================== ROOM DETAIL ==================
@login_required
@user_passes_test(admin_only)
def room_detail(request, room_id):

    room = get_object_or_404(Room, id=room_id)
    contract = Contract.objects.filter(room=room).first()
    tenant = contract.tenant if contract else None

    return render(request, 'room_detail.html', {
        'room': room,
        'tenant': tenant,
        'contract': contract
    })


# ================== QR ==================
def generate_qr(request, bill_id):

    bill = get_object_or_404(Bill, id=bill_id)

    phone = "0630748705"
    phone = phone.replace("-", "")
    if phone.startswith("0"):
        phone = "66" + phone[1:]

    amount = int(bill.total)

    payload = (
        "000201010211"
        "29370016A000000677010111"
        "01130066" + phone +
        "5802TH5303764"
        "54" + str(len(str(amount))).zfill(2) + str(amount) +
        "6304"
    )

    img = qrcode.make(payload)

    buffer = BytesIO()
    img.save(buffer, format="PNG")

    return HttpResponse(buffer.getvalue(), content_type="image/png")


# ================== PDF ==================
def bill_pdf(request, bill_id):

    bill = get_object_or_404(Bill, id=bill_id)

    buffer = BytesIO()

    import os
    from django.conf import settings

    font_path = os.path.join(settings.BASE_DIR, 'fonts/Sarabun/Sarabun-Regular.ttf')

    pdfmetrics.registerFont(TTFont('Sarabun', font_path))

    doc = SimpleDocTemplate(buffer, pagesize=A4)

    styles = getSampleStyleSheet()
    style = styles["Normal"]
    style.fontName = 'Sarabun'
    style.fontSize = 16

    elements = []

    elements.append(Paragraph("ใบเสร็จค่าเช่าห้อง", style))
    elements.append(Spacer(1, 15))

    elements.append(Paragraph(f"เดือน: {bill.month}/{bill.year}", style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph(f"ค่าห้อง: {bill.room_price} บาท", style))
    elements.append(Paragraph(f"ค่าน้ำ: {bill.water_total} บาท", style))
    elements.append(Paragraph(f"ค่าไฟ: {bill.electric_total} บาท", style))

    elements.append(Spacer(1, 15))
    elements.append(Paragraph(f"รวมทั้งหมด: {bill.total} บาท", style))

    doc.build(elements)

    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type='application/pdf')