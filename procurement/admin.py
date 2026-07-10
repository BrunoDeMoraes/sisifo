from django.contrib import admin
from .models import Servidor
from .models import Processo
from .models import Origem
from .models import Setor
from .models import Termo
from .models import Item
from .models import Produto
from .models import Servico
from .models import Conta
from .models import Recurso
from .models import Regular
from .models import Emenda

admin.site.register(Servidor)
admin.site.register(Processo)
admin.site.register(Origem)
admin.site.register(Setor)
admin.site.register(Termo)
admin.site.register(Item)
admin.site.register(Produto)
admin.site.register(Servico)
admin.site.register(Conta)
admin.site.register(Recurso)
admin.site.register(Regular)
admin.site.register(Emenda) 