"""Empty migration preserving history after fixing duplicate fields.

This migration originally attempted to add an ``is_haramain`` field to
``RecruitmentEmployee`` and ``EmployeeEvaluation`` even though the field was
already created in ``0010_add_is_haramain``. When running tests the second
``AddField`` operation triggered a ``ProgrammingError`` because the column
already existed in the database.  The operations have been removed so this
file simply acts as a no-op while still satisfying the dependency chain for
older merge migrations.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_merge_20250618_1324'),
    ]

    operations = []
