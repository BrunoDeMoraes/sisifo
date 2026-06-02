from django.contrib import admin
from .models import Servidor
from .models import Processo
from .models import Origem
from .models import Setor

admin.site.register(Servidor)
admin.site.register(Processo)
admin.site.register(Origem)
admin.site.register(Setor)