from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_department_section_foreignkeys'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RecruitmentEmployee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='الاسم')),
                ('nationality', models.CharField(max_length=50, verbose_name='الجنسية')),
                ('official_job', models.CharField(max_length=100, verbose_name='المهنة الرسمي')),
                ('actual_job', models.CharField(max_length=100, verbose_name='المهنة الفعلية')),
                ('computer_number', models.CharField(max_length=50, verbose_name='رقم الكمبيوتر')),
                ('project_name', models.CharField(max_length=100, verbose_name='اسم المشروع')),
                ('start_date', models.DateField(verbose_name='تاريخ المباشرة')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'موظف استقدام',
                'verbose_name_plural': 'موظفو الاستقدام',
            },
        ),
        migrations.CreateModel(
            name='EmployeeEvaluation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appearance_score', models.PositiveSmallIntegerField(verbose_name='المظهر')),
                ('experience_score', models.PositiveSmallIntegerField(verbose_name='الخبرة')),
                ('skills_score', models.PositiveSmallIntegerField(verbose_name='المهارات الفنية')),
                ('notes', models.TextField(blank=True, verbose_name='ملاحظات')),
                ('evaluation_photo', models.ImageField(blank=True, null=True, upload_to='evaluation_photos/', verbose_name='صورة التقييم')),
                ('orientation_photo', models.ImageField(blank=True, null=True, upload_to='orientation_photos/', verbose_name='صورة المحاضرة')),
                ('evaluated_at', models.DateTimeField(auto_now_add=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evaluations', to='core.recruitmentemployee', verbose_name='الموظف')),
                ('evaluator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='المقيّم')),
            ],
            options={
                'verbose_name': 'تقييم موظف',
                'verbose_name_plural': 'تقييمات الموظفين',
            },
        ),
    ]
