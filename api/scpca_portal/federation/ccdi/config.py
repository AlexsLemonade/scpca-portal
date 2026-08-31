"""
Static placeholder content for the CCDI node's config-driven endpoints.

These values stand in until external onboarding assigns real identifiers and the
data-aware endpoints land; they are intentionally not read from any model.
"""

# GET /info — see `responses.Information` in the spec.
INFO = {
    "server": {
        "name": "ScPCA Portal CCDI Node",
        "owner": "Alex's Lemonade Stand Foundation",
        "contact_email": "ccdl@alexslemonade.org",
        "about_url": "https://scpca.alexslemonade.org",
        "repository_url": "https://github.com/AlexsLemonade/scpca-portal",
        "issues_url": "https://github.com/AlexsLemonade/scpca-portal/issues",
    },
    "api": {
        "api_version": "v1.3.0",
        "documentation_url": "https://cbiit.github.io/ccdi-federation-api/specification.html",
    },
    "data": {
        "version": {"about": "Initial ScPCA CCDI data version.", "version": 1},
        "last_updated": "2026-01-01T00:00:00Z",
        "wiki_url": "https://cbiit.github.io/ccdi-federation-api",
        "documentation_url": "https://scpca.readthedocs.io/en/stable/",
    },
}

# GET /organization[/{name}] — see `models.Organization` in the spec.
ORGANIZATION = {
    "identifier": "alsf",
    "name": "Alex's Lemonade Stand Foundation",
}

# GET /namespace[/{organization}/{namespace}] — see `models.Namespace` in the spec.
NAMESPACE = {
    "id": {"organization": ORGANIZATION["identifier"], "name": "scpca"},
    "description": (
        "Single-cell Pediatric Cancer Atlas (ScPCA) data contributed by "
        "Alex's Lemonade Stand Foundation."
    ),
    "contact_email": "ccdl@alexslemonade.org",
}
