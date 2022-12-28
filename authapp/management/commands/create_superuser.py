from django.core.management.base import BaseCommand, CommandError
import json
import os
from django.conf import settings
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open(os.path.join(settings.BASE_DIR, 'secret.json')) as f:
            data = json.load(f)
        user = get_user_model()
        try:
            user.objects.create_superuser(
                username=data['SU_USERNAME'],
                email=data['SU_EMAIL'],
                password=data['SU_PASSWORD'],
            )
        except Exception as e:
            print(e)
            raise CommandError('Cannot create superuser')
        else:
            self.stdout.write(self.style.SUCCESS("Successfully created superuser"))
