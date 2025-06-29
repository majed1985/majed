"""Empty migration preserving history after refactor.

This file originally duplicated the model creation found in
``0009_recruitment_models`` which caused ``ProgrammingError`` when the
test database was created.  The operations have been removed so the
migration simply acts as a no-op while still satisfying the dependency
chain for older merge migrations.
"""

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_recruitment_models'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = []
