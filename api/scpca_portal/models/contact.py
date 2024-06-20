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

        try:
            zipped_contact_details = utils.get_csv_zipped_values(project_data, "email", "name")
        except Exception:
            logger.error("Unable to add ambiguous contacts.")
            raise

        for email, name in zipped_contact_details:
            if email in common.IGNORED_INPUT_VALUES:
                continue

            contact_data = {
                "name": name.strip(),
                "email": email.lower().strip(),
                "pi_name": project.pi_name,
            }

            # Handle case where contact is already in db
            if existing_contact := Contact.objects.filter(email=contact_data["email"]).first():
                if existing_contact not in project.contacts.all():
                    project.contacts.add(existing_contact)
                continue

            contacts.append(Contact.get_from_dict(contact_data))

        Contact.objects.bulk_create(contacts)
        project.contacts.add(*contacts)
