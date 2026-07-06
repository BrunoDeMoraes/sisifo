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
        validators=[
            RegexValidator(
                regex=r'^\d+$',
                message='A matrícula deve conter apenas números.',
                code='invalid_matricula'
            )
        ],
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

