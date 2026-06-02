from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator

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
        default=CategoriaChoices.CUSTEIO,
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
