from django.contrib import admin
from home.models import Contact, Feedback
from userLogin.models import Product
# Register your models here.
admin.site.register(Contact)
admin.site.register(Feedback)
admin.site.register(Product)