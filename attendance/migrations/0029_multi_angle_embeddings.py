from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0028_remove_grade'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentfaceembedding',
            name='extra_embeddings',
            field=models.JSONField(default=list, help_text='Additional angle embeddings (list of 512-dim lists)'),
        ),
        migrations.AddField(
            model_name='teacherfaceembedding',
            name='extra_embeddings',
            field=models.JSONField(default=list, help_text='Additional angle embeddings (list of 512-dim lists)'),
        ),
    ]
