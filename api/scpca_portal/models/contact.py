from typing import Dict

from django.db import models

from scpca_portal import common
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

    @staticmethod
    def bulk_create_from_project_data(project_data, project):
        """Creates a list of contact objects and then save them."""
        emails = [
            email.lower().strip()
            for email in project_data["contact_email"].split(common.CSV_MULTI_VALUE_DELIMITER)
        ]
        names = [
            name.strip()
            for name in project_data["contact_name"].split(common.CSV_MULTI_VALUE_DELIMITER)
        ]
        contacts = []

        if len(emails) != len(names):
            logger.error("Unable to add ambiguous contacts.")
            return

        for idx, email in enumerate(emails):
            # Skip contact if already in db
            if Contact.objects.filter(email=email):
                continue

            if email in common.IGNORED_INPUT_VALUES:
                continue

            contact_data = {"name": names[idx], "email": email, "pi_name": project.pi_name}
            contacts.append(Contact.get_from_dict(contact_data))

        Contact.objects.bulk_create(contacts)
        project.contacts.add(*contacts)
