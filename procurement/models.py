from django.db import models

# Create your models here.
class Servidor(models.Model):
    matricula = models.CharField(
        primary_key=True,
        max_length=12,
        verbose_name='Número de Matrícula'
    )
    
    nome = models.CharField(
        max_length=30
    )

    def __str__(self) -> str:
        return f"{self.nome}"


class Processo(models.Model):

    # Chave primária auto gerada
    cotacao = models.AutoField(primary_key=True)

    # Número do processo SEI — único na tabela
    processo_sei = models.CharField(
        max_length=30,
        unique=True,
        verbose_name='Processo SEI',
    )

    # Número do Termo de Referência
    numero_tr = models.CharField(
        max_length=10,
        verbose_name='Número do TR',
    )

    # Setor de origem do Termo de Referência
    origem_tr = models.CharField(
        max_length=20,
        verbose_name='Origem do TR',
    )

    # Órgão executor da cotação
    unidade = models.CharField(
        max_length=20,
        verbose_name='Unidade',
    )

    # Tipo de verba — validação feita na interface
    categoria_economica = models.CharField(
        max_length=30,
        verbose_name='Categoria Econômica',
    )

    # Data de recebimento na unidade
    data = models.DateField(
        verbose_name='Data de Recebimento',
    )

    # FK para o servidor responsável
    servidor = models.ForeignKey(
        'Servidor',
        on_delete=models.PROTECT,
        related_name='processos',
        null=True,
        blank=True,
        verbose_name='Servidor Responsável',
    )

    # Campo textual livre para observações
    observacao = models.TextField(
        blank=True,
        default='',
        verbose_name='Observação',
    )

    # Campos de auditoria
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'processo'
        verbose_name = 'Processo'
        verbose_name_plural = 'Processos'
        ordering = ['-data', 'processo_sei']
        indexes = [
            models.Index(fields=['data'], name='idx_processo_data'),
            models.Index(fields=['servidor'], name='idx_processo_servidor'),
            models.Index(fields=['categoria_economica'], name='idx_processo_categoria'),
        ]

    def __str__(self):
        return f'Processo SEI {self.processo_sei} — Cotação #{self.cotacao}'
