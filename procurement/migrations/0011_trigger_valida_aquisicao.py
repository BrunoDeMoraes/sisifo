from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('procurement', '0010_limiteanual_aquisicao_logaquisicao_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE TRIGGER valida_servico_aquisicao_insert
                BEFORE INSERT ON aquisicao
                WHEN NEW.id_servico IS NOT NULL
                BEGIN
                    SELECT CASE
                        WHEN (SELECT tipo FROM item WHERE id_item = NEW.id_item) != 'SV'
                        THEN RAISE(ABORT, 'O campo id_servico só pode ser preenchido para itens do tipo Serviço')
                        WHEN (SELECT id_item FROM servico WHERE id_servico = NEW.id_servico) != NEW.id_item
                        THEN RAISE(ABORT, 'O serviço indicado não pertence ao item selecionado')
                    END;
                END;

                CREATE TRIGGER valida_servico_aquisicao_update
                BEFORE UPDATE ON aquisicao
                WHEN NEW.id_servico IS NOT NULL
                BEGIN
                    SELECT CASE
                        WHEN (SELECT tipo FROM item WHERE id_item = NEW.id_item) != 'SV'
                        THEN RAISE(ABORT, 'O campo id_servico só pode ser preenchido para itens do tipo Serviço')
                        WHEN (SELECT id_item FROM servico WHERE id_servico = NEW.id_servico) != NEW.id_item
                        THEN RAISE(ABORT, 'O serviço indicado não pertence ao item selecionado')
                    END;
                END;

                CREATE TRIGGER valida_quantidade_aquisicao_insert
                BEFORE INSERT ON aquisicao
                WHEN NEW.quantidade_adquirida IS NOT NULL
                BEGIN
                    SELECT CASE
                        WHEN NEW.quantidade_adquirida > NEW.quantidade_solicitada
                        THEN RAISE(ABORT, 'A quantidade adquirida não pode ser superior à quantidade solicitada')
                    END;
                END;

                CREATE TRIGGER valida_quantidade_aquisicao_update
                BEFORE UPDATE ON aquisicao
                WHEN NEW.quantidade_adquirida IS NOT NULL
                BEGIN
                    SELECT CASE
                        WHEN NEW.quantidade_adquirida > NEW.quantidade_solicitada
                        THEN RAISE(ABORT, 'A quantidade adquirida não pode ser superior à quantidade solicitada')
                    END;
                END;
            """,
            reverse_sql="""
                DROP TRIGGER IF EXISTS valida_servico_aquisicao_insert;
                DROP TRIGGER IF EXISTS valida_servico_aquisicao_update;
                DROP TRIGGER IF EXISTS valida_quantidade_aquisicao_insert;
                DROP TRIGGER IF EXISTS valida_quantidade_aquisicao_update;
            """
        ),
    ]
