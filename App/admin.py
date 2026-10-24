from django.contrib import admin
from .models import Incident,UserAccount,OtherIncident
# Register your models here.

admin.site.register(Incident)
admin.site.register(UserAccount)
admin.site.register(OtherIncident)