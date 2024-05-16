from typing import Dict

from django.db import models

from scpca_portal import common, utils
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models.base import TimestampedModel

logger = get_and_configure_logger(__name__)


class Contact(TimestampedModel):
    """Contact class."""

    class Meta:
        db_table = "contacts"

    name = models.TextField()
    email = models.EmailField(unique=True)
    pi_name = models.TextField()

    def __str__(self) -> str:
        return f"{self.name} <{self.email}>"

    @classmethod
    def get_from_dict(cls, data: Dict):
        contact = cls(
            name=data.get("name"),
            email=data.get("email"),
            pi_name=data.get("pi_name"),
        )

        return contact

    @classmethod
    def bulk_create_from_project_data(cls, project_data, project):
        """Creates a list of contact objects and saves them."""
        contacts = []

        keys = ["contact_email", "contact_name"]
        for email, name in utils.get_csv_zipped_values(
            project_data, *keys, model_name=cls.__name__
        ):
            if email in common.IGNORED_INPUT_VALUES:
                continue

            # Skip contact if already in db
            if Contact.objects.filter(email=email):
                continue

            contact_data = {
                "name": name.strip(),
                "email": email.lower().strip(),
                "pi_name": project.pi_name,
            }
            contacts.append(Contact.get_from_dict(contact_data))

        Contact.objects.bulk_create(contacts)
        project.contacts.add(*contacts)
