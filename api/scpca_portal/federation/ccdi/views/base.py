"""Shared base classes for the CCDI federation node views."""

from dataclasses import dataclass, field

from django.core.paginator import Paginator
from rest_framework import status, viewsets
from rest_framework.exceptions import APIException
from rest_framework.permissions import AllowAny

from scpca_portal.federation.ccdi.views.errors import InvalidParameters, node_exception_handler

# The spec lets each server pick its own default, and names 100 as the community
# convention where nothing else is more reasonable.
DEFAULT_PER_PAGE = 100

# The spec sets no upper bound, and this is a public, unauthenticated endpoint,
# so one request could otherwise ask the node to build every entity it has. A
# larger `per_page` is clamped to this rather than rejected: the response stays
# valid, its counts stay truthful, and the `link` header pages at the size
# actually used, so a client following links is never inconsistent.
MAX_PER_PAGE = 1000

# Unharmonized metadata is filtered by a key the spec cannot enumerate, since the
# field names are the server's own.
UNHARMONIZED_FILTER_PREFIX = "metadata.unharmonized."

# Named on an InvalidParameters error so a client knows which to correct.
PAGE_PARAMETERS = ["page", "per_page"]


class EndpointNotImplemented(APIException):
    """Raised by endpoints that are routed but whose response isn't built yet."""

    status_code = status.HTTP_501_NOT_IMPLEMENTED
    default_detail = "This CCDI node endpoint is not implemented yet."
    default_code = "not_implemented"


@dataclass(frozen=True)
class Page:
    """One page of an index response: the rows on it, and how to link to the rest."""

    number: int
    per_page: int
    total: int
    # The highest page that exists. At least 1 even when empty, so `first` in the
    # link header always has a `last` to pair with.
    last: int
    rows: list = field(default_factory=list)


def requested_page(request) -> tuple[int, int]:
    """The `page` and `per_page` this request asks for, or a 422."""
    try:
        number = int(request.query_params.get("page", 1))
        per_page = int(request.query_params.get("per_page", DEFAULT_PER_PAGE))
    except (TypeError, ValueError):
        raise InvalidParameters("Both must be integers.", PAGE_PARAMETERS)

    if number < 1 or per_page < 1:
        raise InvalidParameters(
            "Unable to calculate offset; both must be 1 or greater.", PAGE_PARAMETERS
        )

    return number, min(per_page, MAX_PER_PAGE)


def paginate(request, queryset) -> Page:
    """
    The page of `queryset` this request asks for.

    `page` is a 1-based index defaulting to 1. Both parameters are declared with
    a minimum of 0 in the spec, but no offset can be calculated from a zero page
    or a zero page size, which is the spec's own example of a 422. A `per_page`
    above `MAX_PER_PAGE` is clamped rather than rejected.

    A page past the end is not an error: it is empty and its counts say so, which
    is what `LimitOffsetPagination` — the portal's own v1 pagination — answers
    with. The spec says nothing either way; see the open questions.

    Takes the queryset rather than a count so that past-the-end is answered
    without slicing. A page number large enough to overflow Postgres' OFFSET
    would otherwise reach the database and 500 an unauthenticated endpoint.
    """
    number, per_page = requested_page(request)
    paginator = Paginator(queryset, per_page)

    # `Paginator.page()` raises past the end and `get_page()` silently serves the
    # last page instead of the one asked for. Neither is the answer here, and
    # both slice to find out.
    rows = [] if number > paginator.num_pages else list(paginator.page(number).object_list)

    return Page(
        number=number,
        per_page=per_page,
        total=paginator.count,
        last=paginator.num_pages,
        rows=rows,
    )


def requested_filters(request, filters) -> list[str]:
    """
    The spec's filter parameters this request carries.

    Unharmonized fields are filtered under a `metadata.unharmonized.<field>` key
    rather than a name the spec can enumerate, so that one is matched by prefix.
    A query parameter the spec does not declare is not a filter and is ignored.
    """
    return sorted(
        name
        for name in request.query_params
        if name in filters or name.startswith(UNHARMONIZED_FILTER_PREFIX)
    )


def page_link_header(request, page: Page) -> str:
    """
    The `link` header the spec requires on a paged response.

    `first` and `last` are always present; `prev` and `next` only when there is a
    page on that side. Every other query parameter is carried through, so a link
    reproduces the request it came from.
    """
    numbers = {"first": 1, "last": page.last}

    if page.number > 1:
        # Bounded: a request past the end still links back to a page that exists.
        numbers["prev"] = min(page.number - 1, page.last)
    if page.number < page.last:
        numbers["next"] = page.number + 1

    return ", ".join(
        f'<{page_url(request, number, page.per_page)}>; rel="{relation}"'
        for relation, number in numbers.items()
    )


def page_url(request, number: int, per_page: int) -> str:
    """This request's URL, pointed at another page of the same result set."""
    query = request.query_params.copy()
    query["page"] = number
    query["per_page"] = per_page

    return request.build_absolute_uri(f"{request.path}?{query.urlencode()}")


class CCDINodeViewMixin:
    """Shared config for node views: a public, unauthenticated discovery API."""

    authentication_classes: list = []
    permission_classes = [AllowAny]

    def get_exception_handler(self):
        """
        Render failures as the spec's `responses.Errors` rather than DRF's
        `{"detail": …}`. Returned per view, so v1 keeps DRF's default.
        """
        return node_exception_handler


class EntityViewSet(CCDINodeViewMixin, viewsets.ViewSet):
    """
    Shared endpoint surface for the CCDI primary entities (subject/sample/file):
    list, retrieve, by/{field}/count, and summary. An entity implements the ones
    it serves; the rest answer 501 until they are built.
    """

    def list(self, request):
        raise EndpointNotImplemented()

    def retrieve(self, request, organization=None, namespace=None, name=None):
        raise EndpointNotImplemented()

    def count(self, request, field=None):
        """GET /{entity}/by/{field}/count"""
        raise EndpointNotImplemented()

    def summary(self, request):
        """GET /{entity}/summary"""
        raise EndpointNotImplemented()
