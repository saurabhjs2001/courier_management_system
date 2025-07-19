from django.db import models

# Create your models here.

class Client(models.Model):
    name = models.CharField(max_length=100 ,default='')
    gst_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(max_length=100, blank=False, default='')
    phone = models.CharField(max_length=15)
    fuel_surcharge_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    address = models.TextField()
    
    def __str__(self):
        return self.name
    
    
class Provider(models.Model):
    name = models.CharField(max_length=50, unique=True, default='')
    contact_person = models.CharField(max_length=100, default='')
    phone = models.CharField(max_length=15,default='')
    email = models.EmailField(blank=False, null=False, default='')
    
    def __str__(self):
        return self.name
    
class Shipments(models.Model):

    date = models.DateField()
    document_no = models.CharField(max_length=50, unique=True)
    client_name = models.ForeignKey(Client, on_delete=models.CASCADE)
    service_provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    destination = models.CharField(max_length=150)
    service_type = models.CharField(max_length=10)
    item_type = models.CharField(max_length=10)
    travel_by = models.CharField(max_length=10)
    receiver_name = models.CharField(max_length=100)
    weight = models.FloatField(default=0)
    pcs = models.IntegerField(default=1)
    cost = models.FloatField(default=0)
    
    def __str__(self):
        return f"{self.document_no} - {self.client_name}"  
    
    
     
class Bill(models.Model):
    bill_no = models.CharField(max_length=50, unique=True)
    date = models.DateField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    bill_period_from = models.DateField()
    bill_period_to = models.DateField()
    shipments = models.ManyToManyField(Shipments)
    additional_charges = models.IntegerField(default=0)  # ₹ whole number
    gst_rate = models.IntegerField(default=18)  # e.g., 18 for 18%

    subtotal = models.FloatField(default=0)
    fuel_charge = models.FloatField(default=0)
    gst_amount = models.FloatField(default=0)
    total_amount = models.FloatField(default=0)
    
    def __str__(self):
        return self.bill_no
    @property
    def taxable_amount(self):
        return self.subtotal + self.fuel_charge

    @property
    def cgst(self):
        return round((self.gst_amount / 2), 2)

    @property
    def sgst(self):
        return round((self.gst_amount / 2), 2)