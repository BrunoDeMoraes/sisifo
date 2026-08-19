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
from .models import Fornecedor
from .models import Contato
from .models import Area
from .models import ContatoArea
from .models import Banco
from .models import ContaFornecedor
from .models import LimiteAnual
from .models import Aquisicao
from .models import LogAquisicao
from .models import NotaFiscal
from .models import Pagamento



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
admin.site.register(Fornecedor) 
admin.site.register(Contato)
admin.site.register(Area)
admin.site.register(ContatoArea)
admin.site.register(Banco)
admin.site.register(ContaFornecedor)
admin.site.register(LimiteAnual)
admin.site.register(Aquisicao)
admin.site.register(LogAquisicao)
admin.site.register(NotaFiscal)
admin.site.register(Pagamento)