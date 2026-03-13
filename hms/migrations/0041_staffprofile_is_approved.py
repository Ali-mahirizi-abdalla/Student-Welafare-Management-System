from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('hms', '0040_staffpermission'),
    ]

    operations = [
        migrations.AddField(
            model_name='staffprofile',
            name='is_approved',
            field=models.BooleanField(default=False, help_text='Awaiting Super Admin approval'),
        ),
    ]
