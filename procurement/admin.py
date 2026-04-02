from django.contrib import admin
from .models import Servidor
from .models import Processo

admin.site.register(Servidor)
admin.site.register(Processo)