from django.core.management.base import BaseCommand

from scpca_portal.federation.ccdi.schema.generate import generate


class Command(BaseCommand):
    help = "Regenerate the CCDI node's Pydantic response types from the vendored spec."

    def handle(self, *args, **options):
        generate()
        self.stdout.write(self.style.SUCCESS("Regenerated CCDI response types."))
