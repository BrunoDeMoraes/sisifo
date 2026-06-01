# procurement/management/commands/importar_processos.py

import json
from datetime import datetime
from django.apps import apps
from django.core.management.base import BaseCommand
#from procurement.models import Processo, Servidor
from django.db import models


class Command(BaseCommand):
    help = 'Importa dados da planilha Controle a partir de um arquivo JSON'

    def add_arguments(self, parser):
        parser.add_argument('caminho_json', type=str)

    def handle(self, *args, **options):
        caminho_json = options['caminho_json']

        # Listar modelos disponíveis
        modelo_escolhido = self.escolher_modelo()
        if not modelo_escolhido:
            return

        with open(caminho_json, 'r', encoding='utf-8') as arquivo:
            dados = json.load(arquivo)

        if not dados:
            self.stdout.write(self.style.ERROR("Arquivo JSON vazio ou inválido."))
            return

        # Mostrar chaves disponíveis no JSON
        chaves_json = list(dados[0].keys()) if isinstance(dados, list) else list(dados.keys())
        self.stdout.write(self.style.SUCCESS(f"\nChaves disponíveis no JSON: {', '.join(chaves_json)}"))

        # Obter campos do modelo
        campos_modelo = self.obter_campos_modelo(modelo_escolhido)

        # Criar mapeamento entre campos do modelo e chaves do JSON
        mapeamento = self.criar_mapeamento(campos_modelo, chaves_json)

        # Confirmar importação
        self.stdout.write(self.style.WARNING("\n=== Mapeamento Configurado ==="))
        for campo, info in mapeamento.items():
            chave_json = info['chave_json']
            self.stdout.write(f"  {campo} ← {chave_json}")

        confirma = input("\nDeseja prosseguir com a importação? (s/n): ")
        if confirma.lower() != 's':
            self.stdout.write(self.style.WARNING("Importação cancelada."))
            return

        # Processar importação
        self.importar_dados(modelo_escolhido, dados, mapeamento)


    def escolher_modelo(self):
        """Lista modelos disponíveis e permite escolha do usuário"""
        app_config = apps.get_app_config('procurement')
        modelos = app_config.get_models()

        self.stdout.write(self.style.SUCCESS("\n=== Modelos Disponíveis ==="))
        modelos_lista = []
        for idx, modelo in enumerate(modelos, 1):
            modelos_lista.append(modelo)
            self.stdout.write(f"{idx}. {modelo.__name__}")

        try:
            escolha = int(input("\nEscolha o número do modelo: "))
            if 1 <= escolha <= len(modelos_lista):
                modelo_escolhido = modelos_lista[escolha - 1]
                self.stdout.write(self.style.SUCCESS(f"Modelo escolhido: {modelo_escolhido.__name__}\n"))
                return modelo_escolhido
            else:
                self.stdout.write(self.style.ERROR("Opção inválida."))
                return None
        except (ValueError, IndexError):
            self.stdout.write(self.style.ERROR("Entrada inválida."))
            return None


    def obter_campos_modelo(self, modelo):
        """Retorna informações sobre os campos do modelo"""
        campos = {}
        for field in modelo._meta.get_fields():
            # Ignora campos de relação reversa
            if isinstance(field, (models.ManyToOneRel, models.ManyToManyRel)):
                continue

            tipo = field.get_internal_type()
            obrigatorio = not field.null and not field.blank and not hasattr(field, 'default')
            
            # Verifica se é chave primária com auto_increment/autofield
            e_pk_auto = field.primary_key and isinstance(field, (models.AutoField, models.BigAutoField))
            
            campos[field.name] = {
                'field': field,
                'tipo': tipo,
                'obrigatorio': obrigatorio,
                'relacao': isinstance(field, models.ForeignKey),
                'pk_auto': e_pk_auto
            }

        return campos


    def criar_mapeamento(self, campos_modelo, chaves_json):
        """Cria mapeamento interativo entre campos do modelo e chaves do JSON"""
        mapeamento = {}

        self.stdout.write(self.style.SUCCESS("\n=== Configuração de Mapeamento ==="))
        self.stdout.write("Para cada campo do modelo, informe a chave correspondente no JSON.")
        self.stdout.write("Deixe em branco para pular o campo (apenas campos não obrigatórios).\n")
        self.stdout.write("Digite x para inserir um valor padrão para o o campo).\n")

        for nome_campo, info in campos_modelo.items():
            field = info['field']
            
            # Pula campos auto-gerados (incluindo PKs auto-incrementadas)
            if field.auto_created or info['pk_auto']:
                self.stdout.write(self.style.NOTICE(
                    f"\nCampo: {nome_campo} ({info['tipo']}) [AUTO-PREENCHIDO] - Pulado"
                ))
                continue

            obrigatorio_str = " [OBRIGATÓRIO]" if info['obrigatorio'] else ""
            tipo_str = f" ({info['tipo']})"
            relacao_str = " [Relação FK]" if info['relacao'] else ""

            self.stdout.write(f"\nCampo: {nome_campo}{tipo_str}{obrigatorio_str}{relacao_str}")
            chave_json = input(f"  Chave JSON: ").strip()
            
            if not chave_json:
                if info['obrigatorio']:
                    self.stdout.write(self.style.ERROR(f"  Campo obrigatório! Não pode ser vazio."))
                    chave_json = input(f"  Chave JSON: ").strip()
                else:
                    self.stdout.write(self.style.WARNING(f"  Campo '{nome_campo}' será ignorado."))
                    continue

            if chave_json not in chaves_json:
                self.stdout.write(self.style.WARNING(f"  Aviso: '{chave_json}' não encontrada no JSON."))

            if chave_json == 'x'.strip():
                chave_json = input(f"  Valor padrão para o campo: ").strip()

            mapeamento[nome_campo] = {
                'chave_json': chave_json,
                'field': field,
                'tipo': info['tipo'],
                'relacao': info['relacao']
            }
        return mapeamento


    ###Continuar leitura daqui
    def importar_dados(self, modelo, dados, mapeamento):
        """Realiza a importação dos dados"""
        inseridos = 0
        ignorados = 0
        erros = 0

        # Determina campo único para evitar duplicatas (se existir)
        campo_unico = None
        for nome_campo, info in mapeamento.items():
            if info['field'].unique:
                campo_unico = nome_campo
                break

        dados_lista = dados if isinstance(dados, list) else [dados]

        for item in dados_lista:
            try:
                # Verifica duplicata se houver campo único
                if campo_unico:
                    chave_json = mapeamento[campo_unico]['chave_json']
                    valor_unico = item.get(chave_json)
                    
                    if modelo.objects.filter(**{campo_unico: valor_unico}).exists():
                        self.stdout.write(self.style.WARNING(
                            f"Ignorado: '{valor_unico}' já existe."
                        ))
                        ignorados += 1
                        continue

                # Preparar dados para criação
                dados_objeto = {}
                
                for nome_campo, info in mapeamento.items():
                    if info['chave_json'] not in item.keys():
                        valor = info['chave_json']
                    else:
                        chave_json = info['chave_json']
                        valor = item.get(chave_json)

                    # Converter valor conforme o tipo do campo
                    valor_convertido = self.converter_valor(valor, info)
                    
                    if valor_convertido is not None:
                        dados_objeto[nome_campo] = valor_convertido

                # Criar objeto (ORM do Django gerencia PKs auto-incrementadas automaticamente)
                objeto_criado = modelo.objects.create(**dados_objeto)
                
                valor_exibir = dados_objeto.get(campo_unico) if campo_unico else f"ID {objeto_criado.pk}"
                self.stdout.write(self.style.SUCCESS(f"Inserido: '{valor_exibir}'"))
                inseridos += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erro ao processar item: {str(e)}"))
                erros += 1

        self.stdout.write(self.style.SUCCESS(
            f"\n=== Concluído ===\nInseridos: {inseridos} | Ignorados: {ignorados} | Erros: {erros}"
        ))    


    def converter_valor(self, valor, info):
        """Converte o valor conforme o tipo do campo"""
        if valor is None or valor == '':
            return None

        tipo = info['tipo']

        try:
            if tipo == 'DateField':
                return datetime.fromisoformat(str(valor)).date()
            elif tipo == 'DateTimeField':
                return datetime.fromisoformat(str(valor))
            elif tipo == 'IntegerField':
                return int(valor)
            elif tipo == 'FloatField' or tipo == 'DecimalField':
                return float(valor)
            elif tipo == 'BooleanField':
                return bool(valor)
            elif tipo == 'ForeignKey':
                # Para FK, assume que o valor é o nome ou ID do objeto relacionado
                if info['relacao']:
                    modelo_relacionado = info['field'].related_model
                    # Tenta buscar por nome ou ID
                    try:
                        if isinstance(valor, int):
                            return modelo_relacionado.objects.get(id=valor)
                        else:
                            # Tenta buscar por um campo 'nome'
                            return modelo_relacionado.objects.get(nome=valor)
                    except modelo_relacionado.DoesNotExist:
                        self.stdout.write(self.style.WARNING(
                            f"Objeto relacionado '{valor}' não encontrado."
                        ))
                        return None
            else:
                return str(valor)

        except Exception as e:
            self.stdout.write(self.style.WARNING(
                f"Erro ao converter valor '{valor}' para tipo {tipo}: {str(e)}"
            ))
            return None
