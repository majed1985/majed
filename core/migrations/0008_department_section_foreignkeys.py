from django.db import migrations, models
import django.db.models.deletion


def copy_names_to_fk(apps, schema_editor):
    Learner = apps.get_model("core", "Learner")
    Department = apps.get_model("core", "Department")
    Section = apps.get_model("core", "Section")

    for learner in Learner.objects.all():
        dept_name = getattr(learner, "department")
        sect_name = getattr(learner, "section")

        department = None
        if dept_name:
            department, _ = Department.objects.get_or_create(name=dept_name)

        section = None
        if sect_name and department:
            section, _ = Section.objects.get_or_create(
                name=sect_name,
                department=department,
            )

        learner.department_tmp = department
        learner.section_tmp = section
        learner.save(update_fields=["department_tmp", "section_tmp"])

class Migration(migrations.Migration):
    atomic = False
    dependencies = [
        ('core', '0007_department_section_charfields'),
    ]

    operations = [
        migrations.AddField(
            model_name='learner',
            name='department_tmp',
            field=models.ForeignKey(
                to='core.department',
                on_delete=django.db.models.deletion.SET_NULL,
                null=True,
                blank=True,
                verbose_name='الإدارة',
            ),
        ),
        migrations.AddField(
            model_name='learner',
            name='section_tmp',
            field=models.ForeignKey(
                to='core.section',
                on_delete=django.db.models.deletion.SET_NULL,
                null=True,
                blank=True,
                verbose_name='القسم',
            ),
        ),
        migrations.RunPython(copy_names_to_fk, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='learner',
            name='department',
        ),
        migrations.RemoveField(
            model_name='learner',
            name='section',
        ),
        migrations.RenameField(
            model_name='learner',
            old_name='department_tmp',
            new_name='department',
        ),
        migrations.RenameField(
            model_name='learner',
            old_name='section_tmp',
            new_name='section',
        ),
    ]
