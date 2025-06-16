from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0005_alter_learner_options_alter_section_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='learner',
            name='manager',
            field=models.CharField(
                max_length=50,
                verbose_name='المدير المباشر',
                null=True,
                blank=True,
            ),
        ),
    ]
