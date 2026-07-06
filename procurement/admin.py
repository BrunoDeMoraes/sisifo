from django.contrib import admin
from .models import Servidor
from .models import Processo
from .models import Origem
from .models import Setor
from .models import Termo
from .models import Item
from .models import Produto
from .models import Servico

admin.site.register(Servidor)
admin.site.register(Processo)
admin.site.register(Origem)
admin.site.register(Setor)
admin.site.register(Termo)
admin.site.register(Item)
admin.site.register(Produto)
admin.site.register(Servico)