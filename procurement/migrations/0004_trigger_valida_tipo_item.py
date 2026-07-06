from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('procurement', '0003_item_produto_servico'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE TRIGGER valida_tipo_produto_insert
                BEFORE INSERT ON produto
                BEGIN
                    SELECT CASE
                        WHEN (SELECT tipo FROM item WHERE id_item = NEW.item_ptr_id) != 'PR'
                        THEN RAISE(ABORT, 'Apenas itens do tipo PR podem ser vinculados a Produto')
                    END;
                END;

                CREATE TRIGGER valida_tipo_produto_update
                BEFORE UPDATE ON produto
                BEGIN
                    SELECT CASE
                        WHEN (SELECT tipo FROM item WHERE id_item = NEW.item_ptr_id) != 'PR'
                        THEN RAISE(ABORT, 'Apenas itens do tipo PR podem ser vinculados a Produto')
                    END;
                END;

                CREATE TRIGGER valida_tipo_servico_insert
                BEFORE INSERT ON servico
                BEGIN
                    SELECT CASE
                        WHEN (SELECT tipo FROM item WHERE id_item = NEW.id_item) != 'SV'
                        THEN RAISE(ABORT, 'Apenas itens do tipo SV podem ser vinculados a Serviço')
                    END;
                END;

                CREATE TRIGGER valida_tipo_servico_update
                BEFORE UPDATE ON servico
                BEGIN
                    SELECT CASE
                        WHEN (SELECT tipo FROM item WHERE id_item = NEW.id_item) != 'SV'
                        THEN RAISE(ABORT, 'Apenas itens do tipo SV podem ser vinculados a Serviço')
                    END;
                END;
            """,
            reverse_sql="""
                DROP TRIGGER IF EXISTS valida_tipo_produto_insert;
                DROP TRIGGER IF EXISTS valida_tipo_produto_update;
                DROP TRIGGER IF EXISTS valida_tipo_servico_insert;
                DROP TRIGGER IF EXISTS valida_tipo_servico_update;
            """
        ),
    ]

