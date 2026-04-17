from django.db import models

class Room(models.Model):
    room_number = models.CharField(max_length=10)
    price = models.IntegerField()

    STATUS_CHOICES = [
        ('ว่าง', 'ว่าง'),
        ('ไม่ว่าง', 'ไม่ว่าง'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ว่าง'
    )

    def __str__(self):
        return self.room_number


class Tenant(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    id_card = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return self.name


class Contract(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.tenant} - {self.room}"


class Bill(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)

    month = models.IntegerField()
    year = models.IntegerField()

    room_price = models.FloatField(default=0)

    # น้ำ
    water_old = models.IntegerField(default=0)
    water_new = models.IntegerField(default=0)
    water_unit_price = models.FloatField(default=10)
    water_total = models.FloatField(default=0)

    # ไฟ
    electric_old = models.IntegerField(default=0)
    electric_new = models.IntegerField(default=0)
    electric_unit_price = models.FloatField(default=5)
    electric_total = models.FloatField(default=0)

    # รวม
    total = models.FloatField(default=0)

    # ✅ เพิ่มตรงนี้ (สำคัญ)
    slip = models.ImageField(upload_to='slips/', null=True, blank=True)

    def save(self, *args, **kwargs):
        water_unit = self.water_new - self.water_old
        self.water_total = water_unit * self.water_unit_price

        electric_unit = self.electric_new - self.electric_old
        self.electric_total = electric_unit * self.electric_unit_price

        self.room_price = self.contract.room.price
        self.total = self.room_price + self.water_total + self.electric_total

        super().save(*args, **kwargs)

    @property
    def water_unit(self):
        return self.water_new - self.water_old

    @property
    def electric_unit(self):
        return self.electric_new - self.electric_old

    def __str__(self):
        return f"{self.month}/{self.year}"


class Maintenance(models.Model):

    STATUS_CHOICES = [
        ('รอดำเนินการ', 'รอดำเนินการ'),
        ('กำลังดำเนินการ', 'กำลังดำเนินการ'),
        ('เสร็จแล้ว', 'เสร็จแล้ว'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    detail = models.TextField()

    image = models.ImageField(upload_to='repair/', null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='รอดำเนินการ'
    )

    request_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.detail