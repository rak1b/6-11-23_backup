import json
from django.core.management.base import BaseCommand
from utility.models import District, PostCode, Division,Upazilla
import os
from coreapp.management.commands.utils.setup_utils import LoadRedexLocationData
from decouple import config
local = config("LIVE",default=False,cast=bool)


class Command(BaseCommand):
    help = 'Insert data from JSON into Django models'

    def handle(self, *args, **options):
        # Load JSON data into Python dictionaries
        LoadRedexLocationData()

        self.stdout.write(self.style.SUCCESS('Data inserted successfully.'))
