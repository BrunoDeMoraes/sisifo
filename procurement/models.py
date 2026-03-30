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