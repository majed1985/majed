from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_recruitmentemployee_evaluation_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='LegacyRecruitmentRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employees', models.CharField(max_length=100, verbose_name='Employees')),
                ('emp_id', models.CharField(max_length=50, verbose_name='Emp. ID')),
                ('evaluation', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Evaliuation')),
                ('result', models.CharField(blank=True, max_length=100, null=True, verbose_name='Result')),
                ('result_expectations', models.CharField(blank=True, max_length=100, null=True, verbose_name='Result Expectations')),
                ('name_ar', models.CharField(blank=True, max_length=100, null=True, verbose_name='Name (Arabic)')),
                ('name_en', models.CharField(blank=True, max_length=100, null=True, verbose_name='Name (English)')),
                ('passport_no', models.CharField(blank=True, max_length=100, null=True, verbose_name='Passport No.')),
                ('nationality', models.CharField(blank=True, max_length=50, null=True, verbose_name='Nationality')),
                ('profession', models.CharField(blank=True, max_length=100, null=True, verbose_name='Profession')),
                ('profession_group', models.CharField(blank=True, max_length=100, null=True, verbose_name='Profession Group')),
                ('sponsor', models.CharField(blank=True, max_length=100, null=True, verbose_name='Sponsor')),
                ('date', models.DateField(blank=True, null=True, verbose_name='Date')),
                ('month', models.CharField(blank=True, max_length=20, null=True, verbose_name='Month')),
                ('month_number', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Month Number')),
                ('sector', models.CharField(blank=True, max_length=100, null=True, verbose_name='Sector')),
                ('team_group', models.CharField(blank=True, max_length=100, null=True, verbose_name='Team Group')),
                ('project', models.CharField(blank=True, max_length=100, null=True, verbose_name='Project')),
                ('management', models.CharField(blank=True, max_length=100, null=True, verbose_name='Management')),
                ('project_manager', models.CharField(blank=True, max_length=100, null=True, verbose_name='Project Manager')),
                ('director_of_management', models.CharField(blank=True, max_length=100, null=True, verbose_name='Director of Management')),
                ('year', models.PositiveIntegerField(blank=True, null=True, verbose_name='Year')),
            ],
            options={
                'verbose_name': 'سجل استقدام قديم',
                'verbose_name_plural': 'سجلات الاستقدام القديمة',
            },
        ),
    ]
