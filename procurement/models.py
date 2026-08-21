from datetime import date
from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator


def ano_atual():
    return date.today().year


class Servidor(models.Model):
    id_servidor = models.CharField(
        max_length=20,
        primary_key=True,
        verbose_name="Matrícula",
        help_text="Matrícula funcional do servidor (apenas números)"
    )
    nome = models.CharField(
        max_length=30,
        validators=[MinLengthValidator(3)],
        verbose_name="Nome Completo"
    )
    email = models.EmailField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="E-mail"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )

    class Meta:
        db_table = 'servidor'
        verbose_name = 'Servidor'
        verbose_name_plural = 'Servidores'
        ordering = ['nome']

    def __str__(self):
        return f"{self.id_servidor} - {self.nome}"

    def save(self, *args, **kwargs):
        # Normalização de dados
        self.id_servidor = self.id_servidor.strip()
        self.nome = self.nome.strip().title()
        if self.email:
            self.email = self.email.strip().lower()
        super().save(*args, **kwargs)   


class Processo(models.Model):

    class CategoriaChoices(models.TextChoices):
        CUSTEIO = 'CS', 'Custeio'
        INVESTIMENTO = 'IN', 'Investimento'

    id_processo = models.AutoField(
        primary_key=True,
        verbose_name="ID do Processo"
    )
    numero_sei = models.CharField(
        max_length=30,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d+$',
                message='O número SEI deve conter apenas números.',
                code='invalid_numero_sei'
            )
        ],
        verbose_name="Número SEI"
    )
    categoria = models.CharField(
        max_length=2,
        choices=CategoriaChoices.choices,
        verbose_name="Categoria Econômica"
    )
    data_recebimento = models.DateField(
        verbose_name="Data de Recebimento"
    )
    id_servidor = models.ForeignKey(
        'Servidor',
        on_delete=models.PROTECT,
        db_column='id_servidor',
        verbose_name="Servidor Responsável"
    )
    observacao = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações"
    )
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )

    class Meta:
        db_table = 'processo'
        verbose_name = 'Processo'
        verbose_name_plural = 'Processos'
        ordering = ['-data_recebimento']
        indexes = [
            models.Index(fields=['numero_sei']),
            models.Index(fields=['data_recebimento']),
            models.Index(fields=['id_servidor']),
            models.Index(fields=['categoria']),
        ]

    def __str__(self):
        return f"{self.id_processo} - SEI: {self.numero_sei}"

    def save(self, *args, **kwargs):
        self.numero_sei = self.numero_sei.strip()
        if self.observacao:
            self.observacao = self.observacao.strip()
        super().save(*args, **kwargs)


class Origem(models.Model):
    id_origem = models.AutoField(
        primary_key=True,
        verbose_name="ID da Origem"
    )
    unidade = models.CharField(
        max_length=15,
        unique=True,
        verbose_name="Unidade"
    )
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )

    class Meta:
        db_table = 'origem'
        verbose_name = 'Origem'
        verbose_name_plural = 'Origens'
        ordering = ['unidade']

    def __str__(self):
        return self.unidade

    def save(self, *args, **kwargs):
        self.unidade = self.unidade.strip().upper()
        super().save(*args, **kwargs)


class Setor(models.Model):
    id_setor = models.AutoField(
        primary_key=True,
        verbose_name="ID do Setor"
    )
    id_origem = models.ForeignKey(
        'Origem',
        on_delete=models.PROTECT,
        db_column='id_origem',
        verbose_name="Origem"
    )
    nome_setor = models.CharField(
        max_length=20,
        verbose_name="Nome do Setor"
    )
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )

    class Meta:
        db_table = 'setor'
        verbose_name = 'Setor'
        verbose_name_plural = 'Setores'
        ordering = ['id_origem', 'nome_setor']
        constraints = [
            models.UniqueConstraint(
                fields=['id_origem', 'nome_setor'],
                name='unique_setor_por_origem'
            )
        ]

    def __str__(self):
        return f"{self.id_origem.unidade} - {self.nome_setor}"

    def save(self, *args, **kwargs):
        self.nome_setor = self.nome_setor.strip().upper()
        super().save(*args, **kwargs)


class Termo(models.Model):

    class StatusChoices(models.TextChoices):
        ATIVO = 'AT', 'Ativo'
        INATIVO = 'IN', 'Inativo'

    id_termo = models.AutoField(
        primary_key=True,
        verbose_name="ID do Termo"
    )
    id_processo = models.ForeignKey(
        'Processo',
        on_delete=models.PROTECT,
        db_column='id_processo',
        verbose_name="Processo"
    )
    id_setor = models.ForeignKey(
        'Setor',
        on_delete=models.PROTECT,
        db_column='id_setor',
        verbose_name="Setor"
    )
    rotulo = models.CharField(
        max_length=6,
        verbose_name="Rótulo"
    )
    ano = models.IntegerField(
        default=ano_atual,
        verbose_name="Ano"
    )
    status = models.CharField(
        max_length=2,
        choices=StatusChoices.choices,
        default=StatusChoices.ATIVO,
        verbose_name="Status"
    )
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )

    class Meta:
        db_table = 'termo'
        verbose_name = 'Termo'
        verbose_name_plural = 'Termos'
        ordering = ['-ano', 'rotulo']
        constraints = [ 
            models.UniqueConstraint(
                fields=['id_setor', 'rotulo', 'ano'],
                name='unique_rotulo_por_setor_e_ano'
            )
        ]
        indexes = [
            models.Index(fields=['id_processo']),
            models.Index(fields=['status']),
            models.Index(fields=['ano']),
        ]

    def __str__(self):
        return f"Termo {self.rotulo}/{self.ano}"

    def save(self, *args, **kwargs):
        self.rotulo = self.rotulo.strip()
        if self.status == self.StatusChoices.ATIVO:
            Termo.objects.filter(
                id_processo=self.id_processo,
                status=self.StatusChoices.ATIVO
            ).exclude(pk=self.pk).update(status=self.StatusChoices.INATIVO)
        super().save(*args, **kwargs)


class Item(models.Model):

    class TipoChoices(models.TextChoices):
        PRODUTO = 'PR', 'Produto'
        SERVICO = 'SV', 'Serviço'

    id_item = models.AutoField(
        primary_key=True,
        verbose_name="ID do Item"
    )
    codigo = models.CharField(
        max_length=15,
        unique=True,
        verbose_name="Código"
    )
    descricao = models.TextField(
        verbose_name="Descrição"
    )
    tipo = models.CharField(
        max_length=2,
        choices=TipoChoices.choices,
        verbose_name="Tipo"
    )
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )

    class Meta:
        db_table = 'item'
        verbose_name = 'Item'
        verbose_name_plural = 'Itens'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.descricao}"

    def save(self, *args, **kwargs):
        self.codigo = self.codigo.strip().upper()
        self.descricao = self.descricao.strip()
        super().save(*args, **kwargs)


class Produto(Item):
    apresentacao = models.CharField(
        max_length=20,
        verbose_name="Apresentação"
    )
    observacao = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações"
    )

    class Meta:
        db_table = 'produto'
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['item_ptr__codigo']

    def __str__(self):
        return f"{self.codigo} - {self.apresentacao}"

    def save(self, *args, **kwargs):
        # Durante criação usa self.tipo diretamente
        # Durante atualização busca o Item pai
        tipo = self.tipo if not self.item_ptr_id else Item.objects.get(pk=self.item_ptr_id).tipo
        if tipo != Item.TipoChoices.PRODUTO:
            raise ValueError('Apenas itens do tipo PR podem ser vinculados a Produto')
        self.apresentacao = self.apresentacao.strip()
        if self.observacao:
            self.observacao = self.observacao.strip()
        super().save(*args, **kwargs)


class Servico(models.Model):
    id_servico = models.AutoField(
        primary_key=True,
        verbose_name="ID do Serviço"
    )
    id_item = models.ForeignKey(
        'Item',
        on_delete=models.PROTECT,
        db_column='id_item',
        verbose_name="Item"
    )
    patrimonio = models.CharField(
        max_length=15,
        verbose_name="Patrimônio"
    )
    descricao_patrimonio = models.TextField(
        verbose_name="Descrição do Patrimônio"
    )
    observacao = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações"
    )
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )

    class Meta:
        db_table = 'servico'
        verbose_name = 'Serviço'
        verbose_name_plural = 'Serviços'
        ordering = ['id_item', 'patrimonio']
        constraints = [
            models.UniqueConstraint(
                fields=['id_item', 'patrimonio'],
                name='unique_patrimonio_por_item'
            )
        ]

    def __str__(self):
        return f"{self.id_item.codigo} - {self.patrimonio}"

    def save(self, *args, **kwargs):
        # Busca o Item pai para verificar o tipo
        item = Item.objects.get(pk=self.id_item_id)
        if item.tipo != Item.TipoChoices.SERVICO:
            raise ValueError('Apenas itens do tipo SV podem ser vinculados a Serviço')
        self.patrimonio = self.patrimonio.strip().upper()
        self.descricao_patrimonio = self.descricao_patrimonio.strip()
        if self.observacao:
            self.observacao = self.observacao.strip()
        super().save(*args, **kwargs)


class Conta(models.Model):

    class FuncaoChoices(models.TextChoices):
        PAGAMENTO = 'PG', 'Pagamento'
        TRANSFERENCIA = 'TR', 'Transferência'

    class CategoriaChoices(models.TextChoices):
        CUSTEIO = 'CS', 'Custeio'
        INVESTIMENTO = 'IN', 'Investimento'

    class RecursoChoices(models.TextChoices):
        REGULAR = 'RG', 'Regular'
        EMENDA = 'EM', 'Emenda'

    id_conta = models.AutoField(
        primary_key=True,
        verbose_name="ID da Conta"
    )
    unidade = models.CharField(
        max_length=15,
        verbose_name="Unidade"
    )
    agencia = models.CharField(
        max_length=6,
        verbose_name="Agência"
    )
    numero = models.CharField(
        max_length=10,
        verbose_name="Número"
    )
    cnpj = models.CharField(
        max_length=14,
        validators=[
            RegexValidator(
                regex=r'^\d+$',
                message='O CNPJ deve conter apenas números.',
                code='invalid_cnpj'
            )
        ],
        verbose_name="CNPJ"
    )
    funcao = models.CharField(
        max_length=2,
        choices=FuncaoChoices.choices,
        verbose_name="Função"
    )
    categoria_economica = models.CharField(
        max_length=2,
        choices=CategoriaChoices.choices,
        verbose_name="Categoria Econômica"
    )
    recurso = models.CharField(
        max_length=2,
        choices=RecursoChoices.choices,
        verbose_name="Recurso"
    )
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )

    class Meta:
        db_table = 'conta'
        verbose_name = 'Conta'
        verbose_name_plural = 'Contas'
        ordering = ['unidade']
        constraints = [
            models.UniqueConstraint(
                fields=['unidade', 'agencia', 'numero'],
                name='unique_conta'
            )
        ]

    def __str__(self):
        categoria_nomes = {'CS':'Custeio','IN':'Investimento'}
        recurso_nomes = {'RG': 'Regular', 'EM': 'Emenda'}

        return f"{self.unidade} {categoria_nomes[self.categoria_economica]} / {recurso_nomes[self.recurso]} {self.numero[:-1]}-{self.numero[-1]}"

    def save(self, *args, **kwargs):
        self.unidade = self.unidade.strip().upper()
        self.agencia = self.agencia.strip()
        self.numero = self.numero.strip()
        self.cnpj = self.cnpj.strip()
        super().save(*args, **kwargs)


class Recurso(models.Model):
    id_recurso = models.AutoField(
        primary_key=True,
        verbose_name="ID do Recurso"
    )
    id_conta = models.ForeignKey(
        'Conta',
        on_delete=models.PROTECT,
        db_column='id_conta',
        related_name='recursos',
        verbose_name="Conta"
    )
    exercicio = models.IntegerField(
        default=ano_atual,
        verbose_name="Exercício"
    )
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )

    class Meta:
        db_table = 'recurso'
        verbose_name = 'Recurso'
        verbose_name_plural = 'Recursos'
        ordering = ['-exercicio', 'id_conta']

    def __str__(self):
        return f"{self.id_conta} - {self.exercicio}"

    def save(self, *args, **kwargs):
        # Durante criação usa id_conta_id diretamente
        conta = Conta.objects.filter(pk=self.id_conta_id).first()
        if conta and conta.recurso == Conta.RecursoChoices.REGULAR:
            if Recurso.objects.filter(
                id_conta_id=self.id_conta_id,
                exercicio=self.exercicio
            ).exclude(pk=self.pk).exists():
                raise ValueError(
                    'Já existe um recurso regular para esta conta neste exercício'
                )
        super().save(*args, **kwargs)



class Emenda(Recurso):
    oficio = models.CharField(
        max_length=10,
        verbose_name="Ofício"
    )
    numero = models.CharField(
        max_length=12,
        verbose_name="Número"
    )
    valor = models.DecimalField(
        max_digits=11,
        decimal_places=2,
        verbose_name="Valor"
    )
    parlamentar = models.CharField(
        max_length=30,
        verbose_name="Parlamentar"
    )
    destinacao = models.TextField(
        verbose_name="Destinação"
    )
    data_recebimento = models.DateField(
        verbose_name="Data de Recebimento"
    )
    extrato = models.CharField(
        max_length=40,
        blank=True,
        null=True,
        verbose_name="Extrato"
    )
    sei = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\d+$',
                message='O SEI deve conter apenas números.',
                code='invalid_sei'
            )
        ],
        verbose_name="SEI"
    )
    observacao = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações"
    )

    class Meta:
        db_table = 'emenda'
        verbose_name = 'Emenda'
        verbose_name_plural = 'Emendas'
        ordering = ['-recurso_ptr__exercicio', 'parlamentar']

    def __str__(self):
        return f"Emenda {self.numero} - {self.parlamentar}"

    def save(self, *args, **kwargs):
        # Busca a conta via recurso pai se existir, senão usa id_conta_id diretamente
        if self.recurso_ptr_id:
            recurso = Recurso.objects.filter(pk=self.recurso_ptr_id).first()
            conta = Conta.objects.filter(pk=recurso.id_conta_id).first() if recurso else None
        else:
            conta = Conta.objects.filter(pk=self.id_conta_id).first()
        
        if conta and conta.recurso != Conta.RecursoChoices.EMENDA:
            raise ValueError('Emendas só podem ser vinculadas a contas do tipo Emenda')
        
        self.oficio = self.oficio.strip().upper()
        self.numero = self.numero.strip().upper()
        self.parlamentar = self.parlamentar.strip().title()
        self.destinacao = self.destinacao.strip()
        if self.sei:
            self.sei = self.sei.strip()
        if self.extrato:
            self.extrato = self.extrato.strip()
        if self.observacao:
            self.observacao = self.observacao.strip()
        super().save(*args, **kwargs)



class Regular(models.Model):
    id_regular = models.AutoField(
        primary_key=True,
        verbose_name="ID do Regular"
    )
    id_recurso = models.ForeignKey(
        'Recurso',
        on_delete=models.PROTECT,
        db_column='id_recurso',
        verbose_name="Recurso"
    )
    valor = models.DecimalField(
        max_digits=11,
        decimal_places=2,
        verbose_name="Valor"
    )
    data_recebimento = models.DateField(
        verbose_name="Data de Recebimento"
    )
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )

    class Meta:
        db_table = 'regular'
        verbose_name = 'Regular'
        verbose_name_plural = 'Regulares'
        ordering = ['-data_recebimento']
        constraints = [
            models.UniqueConstraint(
                fields=['id_recurso', 'valor', 'data_recebimento'],
                name='unique_regular'
            )
        ]

    def __str__(self):
        return f"{self.id_recurso} - {self.valor}"

    def save(self, *args, **kwargs):
        # Valida tipo da Conta
        if self.id_recurso.id_conta.recurso != Conta.RecursoChoices.REGULAR:
            raise ValueError('Recursos regulares só podem ser vinculados a contas do tipo Regular')
        super().save(*args, **kwargs)


class Fornecedor(models.Model):

    class UFChoices(models.TextChoices):
        AC = 'AC', 'Acre'
        AL = 'AL', 'Alagoas'
        AP = 'AP', 'Amapá'
        AM = 'AM', 'Amazonas'
        BA = 'BA', 'Bahia'
        CE = 'CE', 'Ceará'
        DF = 'DF', 'Distrito Federal'
        ES = 'ES', 'Espírito Santo'
        GO = 'GO', 'Goiás'
        MA = 'MA', 'Maranhão'
        MT = 'MT', 'Mato Grosso'
        MS = 'MS', 'Mato Grosso do Sul'
        MG = 'MG', 'Minas Gerais'
        PA = 'PA', 'Pará'
        PB = 'PB', 'Paraíba'
        PR = 'PR', 'Paraná'
        PE = 'PE', 'Pernambuco'
        PI = 'PI', 'Piauí'
        RJ = 'RJ', 'Rio de Janeiro'
        RN = 'RN', 'Rio Grande do Norte'
        RS = 'RS', 'Rio Grande do Sul'
        RO = 'RO', 'Rondônia'
        RR = 'RR', 'Roraima'
        SC = 'SC', 'Santa Catarina'
        SP = 'SP', 'São Paulo'
        SE = 'SE', 'Sergipe'
        TO = 'TO', 'Tocantins'

    id_fornecedor = models.AutoField(
        primary_key=True,
        verbose_name="ID do Fornecedor"
    )
    cnpj_fornecedor = models.CharField(
        max_length=14,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d+$',
                message='O CNPJ deve conter apenas números.',
                code='invalid_cnpj'
            )
        ],
        verbose_name="CNPJ"
    )
    razao_social = models.CharField(
        max_length=100,
        verbose_name="Razão Social"
    )
    nome_fantasia = models.CharField(
        max_length=40,
        verbose_name="Nome Fantasia"
    )
    codigo_sis = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Código SIS"
    )
    uf = models.CharField(
        max_length=2,
        choices=UFChoices.choices,
        verbose_name="UF"
    )
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )

    class Meta:
        db_table = 'fornecedor'
        verbose_name = 'Fornecedor'
        verbose_name_plural = 'Fornecedores'
        ordering = ['razao_social']

    def __str__(self):
        return f"{self.cnpj_fornecedor} - {self.razao_social}"

    def save(self, *args, **kwargs):
        self.cnpj_fornecedor = self.cnpj_fornecedor.strip()
        self.razao_social = self.razao_social.strip().upper()
        self.nome_fantasia = self.nome_fantasia.strip().upper()
        if self.codigo_sis:
            self.codigo_sis = self.codigo_sis.strip().upper()
        super().save(*args, **kwargs)


class Contato(models.Model):
    id_contato = models.AutoField(
        primary_key=True,
        verbose_name="ID do Contato"
    )
    cnpj_fornecedor = models.ForeignKey(
        'Fornecedor',
        on_delete=models.PROTECT,
        db_column='cnpj_fornecedor',
        to_field='cnpj_fornecedor',
        verbose_name="Fornecedor"
    )
    email = models.EmailField(
        verbose_name="E-mail"
    )
    contato = models.CharField(
        max_length=40,
        verbose_name="Contato"
    )
    telefone = models.CharField(
        max_length=11,
        validators=[
            RegexValidator(
                regex=r'^\d+$',
                message='O telefone deve conter apenas números.',
                code='invalid_telefone'
            )
        ],
        verbose_name="Telefone"
    )
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )

    class Meta:
        db_table = 'contato'
        verbose_name = 'Contato'
        verbose_name_plural = 'Contatos'
        ordering = ['cnpj_fornecedor', 'contato']
        constraints = [
            models.UniqueConstraint(
                fields=['cnpj_fornecedor', 'email'],
                name='unique_email_por_fornecedor'
            )
        ]
        indexes = [
            models.Index(fields=['cnpj_fornecedor']),
        ]

    def __str__(self):
        return f"{self.cnpj_fornecedor} - {self.contato}"

    def save(self, *args, **kwargs):
        self.email = self.email.strip().lower()
        self.contato = self.contato.strip().title()
        self.telefone = self.telefone.strip()
        super().save(*args, **kwargs)


class Area(models.Model):
    id_area = models.AutoField(
        primary_key=True,
        verbose_name="ID da Área"
    )
    atuacao = models.CharField(
        max_length=40,
        unique=True,
        verbose_name="Área de Atuação"
    )
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )

    class Meta:
        db_table = 'area'
        verbose_name = 'Área'
        verbose_name_plural = 'Áreas'
        ordering = ['atuacao']

    def __str__(self):
        return self.atuacao

    def save(self, *args, **kwargs):
        self.atuacao = self.atuacao.strip().upper()
        super().save(*args, **kwargs)


class ContatoArea(models.Model):
    id_contato_area = models.AutoField(
        primary_key=True,
        verbose_name="ID Contato Área"
    )
    id_contato = models.ForeignKey(
        'Contato',
        on_delete=models.PROTECT,
        db_column='id_contato',
        verbose_name="Contato"
    )
    id_area = models.ForeignKey(
        'Area',
        on_delete=models.PROTECT,
        db_column='id_area',
        verbose_name="Área"
    )
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )

    class Meta:
        db_table = 'contato_area'
        verbose_name = 'Contato Área'
        verbose_name_plural = 'Contatos Áreas'
        ordering = ['id_contato', 'id_area']
        constraints = [
            models.UniqueConstraint(
                fields=['id_contato', 'id_area'],
                name='unique_contato_area'
            )
        ]

    def __str__(self):
        return f"{self.id_contato} - {self.id_area}"


class Banco(models.Model):
    id_banco = models.AutoField(
        primary_key=True,
        verbose_name="ID do Banco"
    )
    codigo_compe = models.CharField(
        max_length=3,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d+$',
                message='O código COMPE deve conter apenas números.',
                code='invalid_codigo_compe'
            )
        ],
        verbose_name="Código COMPE"
    )
    nome = models.CharField(
        max_length=40,
        verbose_name="Nome do Banco"
    )
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )

    class Meta:
        db_table = 'banco'
        verbose_name = 'Banco'
        verbose_name_plural = 'Bancos'
        ordering = ['codigo_compe']

    def __str__(self):
        return f"{self.codigo_compe} - {self.nome}"

    def save(self, *args, **kwargs):
        self.codigo_compe = self.codigo_compe.strip()
        self.nome = self.nome.strip().upper()
        super().save(*args, **kwargs)


class ContaFornecedor(models.Model):
    id_conta_fornecedor = models.AutoField(
        primary_key=True,
        verbose_name="ID da Conta Fornecedor"
    )
    id_fornecedor = models.OneToOneField(
        'Fornecedor',
        on_delete=models.PROTECT,
        db_column='id_fornecedor',
        verbose_name="Fornecedor"
    )
    id_banco = models.ForeignKey(
        'Banco',
        on_delete=models.PROTECT,
        db_column='id_banco',
        verbose_name="Banco"
    )
    agencia = models.CharField(
        max_length=6,
        validators=[
            RegexValidator(
                regex=r'^\d+$',
                message='A agência deve conter apenas números.',
                code='invalid_agencia'
            )
        ],
        verbose_name="Agência"
    )
    digito_agencia = models.CharField(
        max_length=1,
        blank=True,
        null=True,
        verbose_name="Dígito da Agência"
    )
    conta = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^\d+$',
                message='A conta deve conter apenas números.',
                code='invalid_conta'
            )
        ],
        verbose_name="Conta"
    )
    digito_conta = models.CharField(
        max_length=1,
        blank=True,
        null=True,
        verbose_name="Dígito da Conta"
    )
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )

    class Meta:
        db_table = 'conta_fornecedor'
        verbose_name = 'Conta Fornecedor'
        verbose_name_plural = 'Contas Fornecedores'
        ordering = ['id_fornecedor']

    def __str__(self):
        return f"{self.id_fornecedor} - {self.id_banco} - {self.agencia}/{self.conta}"

    def save(self, *args, **kwargs):
        self.agencia = self.agencia.strip()
        if self.digito_agencia:
            self.digito_agencia = self.digito_agencia.strip().upper()
        self.conta = self.conta.strip()
        if self.digito_conta:
            self.digito_conta = self.digito_conta.strip().upper()
        super().save(*args, **kwargs)


class LimiteAnual(models.Model):
    id_limite = models.AutoField(
        primary_key=True,
        verbose_name="ID do Limite"
    )
    ano = models.IntegerField(
        unique=True,
        default=ano_atual,
        verbose_name="Ano"
    )
    valor_limite = models.DecimalField(
        max_digits=11,
        decimal_places=2,
        verbose_name="Valor Limite"
    )
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )

    class Meta:
        db_table = 'limite_anual'
        verbose_name = 'Limite Anual'
        verbose_name_plural = 'Limites Anuais'
        ordering = ['-ano']

    def __str__(self):
        return f"Limite {self.ano}: R$ {self.valor_limite}"


class Aquisicao(models.Model):

    id_aquisicao = models.AutoField(
        primary_key=True,
        verbose_name="ID da Aquisição"
    )
    id_termo = models.ForeignKey(
        'Termo',
        on_delete=models.PROTECT,
        db_column='id_termo',
        verbose_name="Termo"
    )
    id_item = models.ForeignKey(
        'Item',
        on_delete=models.PROTECT,
        db_column='id_item',
        verbose_name="Item"
    )
    id_servico = models.ForeignKey(
        'Servico',
        on_delete=models.PROTECT,
        db_column='id_servico',
        blank=True,
        null=True,
        verbose_name="Serviço"
    )
    quantidade_solicitada = models.IntegerField(
        verbose_name="Quantidade Solicitada"
    )
    preco = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        blank=True,
        null=True,
        verbose_name="Preço Unitário"
    )
    quantidade_adquirida = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Quantidade Adquirida"
    )
    id_recurso = models.ForeignKey(
        'Recurso',
        on_delete=models.PROTECT,
        db_column='id_recurso',
        blank=True,
        null=True,
        verbose_name="Recurso"
    )
    id_fornecedor = models.ForeignKey(
        'Fornecedor',
        on_delete=models.PROTECT,
        db_column='id_fornecedor',
        blank=True,
        null=True,
        verbose_name="Fornecedor"
    )
    data_ordem = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data da Ordem de Fornecimento"
    )
    sei_dodf = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\d+$',
                message='O SEI DODF deve conter apenas números.',
                code='invalid_sei_dodf'
            )
        ],
        verbose_name="SEI DODF"
    )
    data_publicacao = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data de Publicação"
    )
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )

    class Meta:
        db_table = 'aquisicao'
        verbose_name = 'Aquisição'
        verbose_name_plural = 'Aquisições'
        ordering = ['-data_cadastro']
        indexes = [
            models.Index(fields=['id_termo']),
            models.Index(fields=['id_item']),
            models.Index(fields=['id_fornecedor']),
            models.Index(fields=['id_recurso']),
            models.Index(fields=['data_ordem']),
        ]

    def __str__(self):
        return f"Aquisição {self.id_aquisicao} - {self.id_item}"

    def save(self, *args, **kwargs):
        from django.db.models import Sum, F
        from decimal import Decimal
        

        # Validação 1: id_servico × tipo do item
        if self.id_servico_id:
            if self.id_item.tipo != Item.TipoChoices.SERVICO:
                raise ValueError(
                    'O campo id_servico só pode ser preenchido para itens do tipo Serviço'
                )
            if self.id_servico.id_item_id != self.id_item_id:
                raise ValueError(
                    'O serviço indicado não pertence ao item selecionado'
                )
        if self.id_item.tipo == Item.TipoChoices.PRODUTO and self.id_servico_id:
            raise ValueError(
                'O campo id_servico não pode ser preenchido para itens do tipo Produto'
            )

        # Validação 2: quantidade_adquirida ≤ quantidade_solicitada
        if self.quantidade_adquirida:
            if self.quantidade_adquirida > self.quantidade_solicitada:
                raise ValueError(
                    'A quantidade adquirida não pode ser superior à quantidade solicitada'
                )

        # Validações financeiras só quando preco e quantidade_adquirida estiverem preenchidos
        if self.preco and self.quantidade_adquirida:
            valor_atual = Decimal(str(self.preco)) * Decimal(self.quantidade_adquirida)
            ano_aquisicao = self.id_termo.ano

            # Validação 3: Limite anual por item
            try:
                limite = LimiteAnual.objects.get(ano=ano_aquisicao)
                soma_item = Aquisicao.objects.filter(
                    id_item=self.id_item,
                    id_termo__ano=ano_aquisicao,
                    preco__isnull=False,
                    quantidade_adquirida__isnull=False
                ).exclude(pk=self.pk).aggregate(
                    total=Sum(F('preco') * F('quantidade_adquirida'))
                )['total'] or 0

                if soma_item + valor_atual > limite.valor_limite:
                    raise ValueError(
                        f'Limite anual de R$ {limite.valor_limite} '
                        f'para este item seria ultrapassado. '
                        f'Valor já utilizado: R$ {soma_item}. '
                        f'Disponível: R$ {limite.valor_limite - soma_item}'
                    )
            except LimiteAnual.DoesNotExist:
                raise ValueError(
                    f'Não há limite anual cadastrado para o ano {ano_aquisicao}'
                )

            # Validação 4: Saldo do recurso
            if self.id_recurso_id:
                soma_recurso = Aquisicao.objects.filter(
                    id_recurso=self.id_recurso,
                    preco__isnull=False,
                    quantidade_adquirida__isnull=False
                ).exclude(pk=self.pk).aggregate(
                    total=Sum(F('preco') * F('quantidade_adquirida'))
                )['total'] or 0

                try:
                    emenda = self.id_recurso.emenda
                    saldo_total = emenda.valor
                except Exception:
                    saldo_total = Regular.objects.filter(
                        id_recurso=self.id_recurso
                    ).aggregate(total=Sum('valor'))['total'] or 0

                if soma_recurso + valor_atual > saldo_total:
                    raise ValueError(
                        f'Saldo insuficiente no recurso indicado. '
                        f'Saldo disponível: R$ {saldo_total - soma_recurso}'
                    )

        # Log de auditoria para id_recurso e id_fornecedor
        if self.pk:
            old = Aquisicao.objects.get(pk=self.pk)
            if old.id_recurso_id != self.id_recurso_id:
                LogAquisicao.objects.create(
                    id_aquisicao=self,
                    campo_alterado='id_recurso',
                    valor_anterior=str(old.id_recurso_id),
                    valor_novo=str(self.id_recurso_id)
                )
            if old.id_fornecedor_id != self.id_fornecedor_id:
                LogAquisicao.objects.create(
                    id_aquisicao=self,
                    campo_alterado='id_fornecedor',
                    valor_anterior=str(old.id_fornecedor_id),
                    valor_novo=str(self.id_fornecedor_id)
                )

        if self.sei_dodf:
            self.sei_dodf = self.sei_dodf.strip()

        super().save(*args, **kwargs)


class LogAquisicao(models.Model):
    id_log = models.AutoField(
        primary_key=True,
        verbose_name="ID do Log"
    )
    id_aquisicao = models.ForeignKey(
        'Aquisicao',
        on_delete=models.PROTECT,
        db_column='id_aquisicao',
        verbose_name="Aquisição"
    )
    campo_alterado = models.CharField(
        max_length=30,
        verbose_name="Campo Alterado"
    )
    valor_anterior = models.TextField(
        blank=True,
        null=True,
        verbose_name="Valor Anterior"
    )
    valor_novo = models.TextField(
        blank=True,
        null=True,
        verbose_name="Valor Novo"
    )
    id_servidor = models.ForeignKey(
        'Servidor',
        on_delete=models.PROTECT,
        db_column='id_servidor',
        blank=True,
        null=True,
        verbose_name="Servidor"
    )
    data_alteracao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data da Alteração"
    )

    class Meta:
        db_table = 'log_aquisicao'
        verbose_name = 'Log de Aquisição'
        verbose_name_plural = 'Logs de Aquisição'
        ordering = ['-data_alteracao']

    def __str__(self):
        return f"Log {self.id_log} - Aquisição {self.id_aquisicao} - {self.campo_alterado}"


class NotaFiscal(models.Model):
    id_nota_fiscal = models.AutoField(
        primary_key=True,
        verbose_name="ID da Nota Fiscal"
    )
    id_fornecedor = models.ForeignKey(
        'Fornecedor',
        on_delete=models.PROTECT,
        db_column='id_fornecedor',
        verbose_name="Fornecedor"
    )
    numero_nf = models.CharField(
        max_length=10,
        verbose_name="Número da Nota Fiscal"
    )
    data_emissao = models.DateField(
        verbose_name="Data de Emissão"
    )
    total_nf = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        verbose_name="Total da Nota Fiscal"
    )
    data_recebimento = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data de Recebimento"
    )
    data_atesto = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data de Atesto"
    )
    reinf = models.BooleanField(
        default=False,
        verbose_name="REINF"
    )
    optante_simples = models.BooleanField(
        blank=True,
        null=True,
        verbose_name="Optante do Simples Nacional"
    )
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )

    class Meta:
        db_table = 'nota_fiscal'
        verbose_name = 'Nota Fiscal'
        verbose_name_plural = 'Notas Fiscais'
        ordering = ['-data_emissao']
        constraints = [
            models.UniqueConstraint(
                fields=['id_fornecedor', 'numero_nf'],
                name='unique_nf_por_fornecedor'
            )
        ]
        indexes = [
            models.Index(fields=['id_fornecedor']),
        ]

    def __str__(self):
        return f"NF {self.numero_nf} - {self.id_fornecedor}"

    def save(self, *args, **kwargs):
        self.numero_nf = self.numero_nf.strip().upper()
        super().save(*args, **kwargs)


class Pagamento(models.Model):
    id_pagamento = models.AutoField(
        primary_key=True,
        verbose_name="ID do Pagamento"
    )
    id_aquisicao = models.ForeignKey(
        'Aquisicao',
        on_delete=models.PROTECT,
        db_column='id_aquisicao',
        verbose_name="Aquisição"
    )
    id_nota_fiscal = models.ForeignKey(
        'NotaFiscal',
        on_delete=models.PROTECT,
        db_column='id_nota_fiscal',
        verbose_name="Nota Fiscal"
    )
    quantidade_paga = models.IntegerField(
        verbose_name="Quantidade Paga"
    )
    numero_pagamento = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Número do Pagamento"
    )
    data_pagamento = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data do Pagamento"
    )
    registro_sei = models.BooleanField(
        default=False,
        verbose_name="Registro SEI"
    )
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )

    class Meta:
        db_table = 'pagamento'
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'
        ordering = ['-data_pagamento']
        constraints = [
            models.UniqueConstraint(
                fields=['id_aquisicao', 'id_nota_fiscal'],
                name='unique_pagamento_por_aquisicao_nf'
            )
        ]
        indexes = [
            models.Index(fields=['id_aquisicao']),
            models.Index(fields=['id_nota_fiscal']),
        ]

    def __str__(self):
        return f"Pagamento {self.id_pagamento} - Aquisição {self.id_aquisicao}"

    def save(self, *args, **kwargs):
        # Validação: quantidade_paga não pode superar quantidade_adquirida
        if self.id_aquisicao.quantidade_adquirida:
            quantidade_ja_paga = Pagamento.objects.filter(
                id_aquisicao=self.id_aquisicao
            ).exclude(pk=self.pk).aggregate(
                total=models.Sum('quantidade_paga')
            )['total'] or 0

            if quantidade_ja_paga + self.quantidade_paga > self.id_aquisicao.quantidade_adquirida:
                raise ValueError(
                    f'Quantidade paga total ({quantidade_ja_paga + self.quantidade_paga}) '
                    f'não pode superar a quantidade adquirida '
                    f'({self.id_aquisicao.quantidade_adquirida})'
                )

        if self.numero_pagamento:
            self.numero_pagamento = self.numero_pagamento.strip().upper()

        super().save(*args, **kwargs)

