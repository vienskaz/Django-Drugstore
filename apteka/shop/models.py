from django.db import models
from typing import Any
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.validators import MinValueValidator

from django.db import models

class ActiveDrug(models.Model):
    name = models.CharField(max_length=50)
    conflicts = models.ManyToManyField('self', symmetrical=True, blank=True)
    
    def __str__(self):
        return self.name

    

class Item(models.Model):
    name = models.CharField(max_length=50)
    active_drug = models.ForeignKey(ActiveDrug,on_delete=models.SET_NULL, blank=True, null=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    image = models.ImageField(upload_to="images", null=True, default="default.jpg")
    slug = models.SlugField(unique=True, db_index=True)
    prescription = models.BooleanField(null=True)
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    dosage = models.CharField(null=True, default=None, max_length=200)


    def __str__(self):
        return self.name
    




class Customer(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    email = models.EmailField(unique=True, null=True)
    first_name = models.CharField(max_length=50, default="")
    last_name = models.CharField(max_length=50, default="")
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    def get_short_name(self):
        return self.first_name or self.email.split("@")[0]

    def __str__(self):
        return str(self.user)

    

class Order(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True)
    

    def __str__(self):
        return str(self.id)

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total
    
class Prescription(models.Model):
    pdf_prescription = models.FileField(upload_to='pdfs/', null=True, blank=True)
    order = models.ForeignKey(
        Order, on_delete=models.SET_NULL, null=True, blank=True)
    


class OrderItem(models.Model):
    item = models.ForeignKey(
        Item, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(
        Order, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.item} X{self.quantity}'

    @property
    def get_total(self):
        total = self.item.price * self.quantity
        return total


class Address(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(
        Order, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=50, null=True)
    country = models.CharField(max_length=50, null=True)
    state = models.CharField(max_length=50, null=True)
    zipcode = models.CharField(max_length=50, null=True)
    date_added = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'


def create_customer(sender, instance, created, **kwargs):
    if created:
        user_customer = Customer(user=instance)
        user_customer.save()


post_save.connect(create_customer, sender=User)
