class JobState:
    CREATED = "CREATED"
    SUBMITTED = "SUBMITTED"
    COMPLETED = "COMPLETED"
    TERMINATED = "TERMINATED"

    CHOICES = (
        (CREATED, "Created"),
        (SUBMITTED, "Submitted"),
        (COMPLETED, "Completed"),
        (COMPLETED, "Terminated"),
    )
