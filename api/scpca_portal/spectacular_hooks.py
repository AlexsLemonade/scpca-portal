"""
drf-spectacular hooks for the ScPCA Portal API schema.

Excludes anything that isn't part of the portal API.
"""

import re

# Portal API routes are version-prefixed (/v1, ...).
_PORTAL_PATH = re.compile(r"^/v[0-9]")


def exclude_non_portal_paths(endpoints):
    """Preprocessing hook: keep only ScPCA Portal routes in the generated schema."""
    return [endpoint for endpoint in endpoints if _PORTAL_PATH.match(endpoint[0])]
