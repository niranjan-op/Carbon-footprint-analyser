from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('Model', '0011_carbonemission_transport_weights'),
    ]

    operations = [
        migrations.AddField(
            model_name='carbonemission',
            name='transport_weights',
            field=models.TextField(blank=True, null=True, default='{}'),
        ),
    ]
