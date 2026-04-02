# procurement/management/commands/importar_processos.py

import json
from datetime import datetime
from django.core.management.base import BaseCommand
from procurement.models import Processo, Servidor


class Command(BaseCommand):
    help = 'Importa dados da planilha Controle a partir de um arquivo JSON'

    def add_arguments(self, parser):
        parser.add_argument('caminho_json', type=str)

    def handle(self, *args, **options):
        caminho_json = options['caminho_json']

        with open(caminho_json, 'r', encoding='utf-8') as arquivo:
            dados = json.load(arquivo)

        inseridos = 0
        ignorados = 0

        for item in dados:
            processo_sei = item.get('Nº de processo SEI')

            if Processo.objects.filter(processo_sei=processo_sei).exists():
                self.stdout.write(self.style.WARNING(
                    f"Ignorado: '{processo_sei}' já existe."
                ))
                ignorados += 1
                continue

            # Busca o servidor pelo nome informado no JSON
            nome_responsavel = item.get('Responsável')
            servidor = None
            try:
                servidor = Servidor.objects.get(nome=nome_responsavel)
            except Servidor.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f"Servidor '{nome_responsavel}' não encontrado. Campo servidor ficará em branco."
                ))

            data_convertida = datetime.fromisoformat(item.get('Recebimento')).date()

            Processo.objects.create(
                processo_sei=processo_sei,
                numero_tr=item.get('TR'),
                origem_tr=item.get('Origem'),
                unidade='HRG',
                categoria_economica='custeio',
                data=data_convertida,
                servidor=servidor,
            )

            self.stdout.write(self.style.SUCCESS(
                f"Inserido: '{processo_sei}'."
            ))
            inseridos += 1

        self.stdout.write(f"\nConcluído. Inseridos: {inseridos} | Ignorados: {ignorados}")