from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0029_multi_angle_embeddings'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentfaceembedding',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='studentfaceembedding',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='teacherfaceembedding',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='teacherfaceembedding',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
