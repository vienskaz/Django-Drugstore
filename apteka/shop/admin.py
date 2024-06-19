from django.contrib import admin
from .models import *


class CustomerInline(admin.StackedInline):
    model = Customer


class UserAdmin(admin.ModelAdmin):
    fields = ["username"]
    inlines = [CustomerInline]


class ItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Address)
admin.site.register(Order)
admin.site.register(Item, ItemAdmin)
admin.site.register(OrderItem)
admin.site.register(Prescription)
admin.site.register(ActiveDrug)

