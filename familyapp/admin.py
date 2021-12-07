from django.contrib import admin

# Register your models here.

from familyapp.models import *

admin.site.register(Members)
admin.site.register(Parent)
admin.site.register(Childrens)