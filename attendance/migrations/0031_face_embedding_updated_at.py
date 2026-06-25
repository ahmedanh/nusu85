from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0030_face_embedding_timestamps'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentfaceembedding',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='teacherfaceembedding',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
