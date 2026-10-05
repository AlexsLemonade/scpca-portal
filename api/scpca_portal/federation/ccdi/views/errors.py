"""
The errors the node returns, in the shape the spec defines.

The spec answers every failure with a `responses.Errors` body — an `errors`
array whose entries are discriminated by `kind` — rather than with DRF's
`{"detail": …}`. Each class below is one kind: it owns its status, the fields
that kind declares, and the message built from them.

Scoping is by inheritance rather than by path. `CCDINodeViewMixin` returns
`node_exception_handler` from `get_exception_handler`, so only views that are
part of the node are affected and v1's error bodies cannot change by accident.
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.exceptions import APIException, MethodNotAllowed
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from scpca_portal.federation.ccdi import schema


class NodeError(APIException):
    """A failure the spec names a `kind` for."""

    kind: str

    def __init__(self, message: str, **fields):
        super().__init__(message)

        self.message = message
        self.fields = fields

    def as_error(self):
        """This failure as one entry of an `errors` array."""
        return schema.error_kind(self.kind, self.message, **self.fields)


class NotFound(NodeError):
    """A route that exists, for a record that does not."""

    kind = "NotFound"
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, entity: str):
        super().__init__(f"{entity} not found.", entity=entity)


class InvalidRoute(NodeError):
    """
    No endpoint matches, including when the path exists but the method does not.

    404 rather than 405 for a wrong method, which is what the spec asks for:
    `InvalidRoute` is documented as covering "all routes for which the path
    exists, but the HTTP method is not supported for that path", and the
    reference implementation answers all of them `404`.
    """

    kind = "InvalidRoute"
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, method: str, route: str):
        super().__init__(f"Invalid route: {method} {route}.", method=method, route=route)


class InvalidParameters(NodeError):
    """Query or path parameters the endpoint cannot act on."""

    kind = "InvalidParameters"
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    def __init__(self, reason: str, parameters: list[str] | None = None):
        # `reason` stands alone as a field, so it is a capitalised sentence and
        # is lowercased only where it is interpolated — which is the shape every
        # example in the spec uses.
        super().__init__(
            f"Invalid value for {_named(parameters)}: {reason[:1].lower()}{reason[1:]}",
            reason=reason,
            parameters=parameters,
        )


def _named(parameters: list[str] | None) -> str:
    """`'page' and 'per_page'`, joined the way the reference implementation does."""
    if not parameters:
        return "the parameters provided"

    quoted = [f"'{name}'" for name in parameters]

    if len(quoted) == 1:
        return f"parameter {quoted[0]}"

    return f"parameters {' and '.join(quoted)}"


def as_body(error: NodeError) -> dict:
    """The `responses.Errors` body for one failure."""
    return schema.dump(schema.ErrorsResponse(errors=[error.as_error()]))


def node_exception_handler(exc, context):
    """
    Render the node's failures as `responses.Errors`.

    DRF raises `MethodNotAllowed` itself, before any of our code runs, so it is
    translated here rather than at a call site. Anything else the node does not
    name a kind for falls through to DRF — today that is only the 501 the
    unimplemented endpoints answer, which the spec does not document either way.
    """
    if isinstance(exc, MethodNotAllowed):
        request = context["request"]
        exc = InvalidRoute(request.method, request.path)

    if isinstance(exc, NodeError):
        return Response(as_body(exc), status=exc.status_code)

    return drf_exception_handler(exc, context)


@csrf_exempt
def invalid_route(request, *args, **kwargs):
    """
    Anything under the node's prefix that matches no endpoint.

    Scoped by where it is mounted — last in the node's own URLconf — so a 404
    anywhere else in the portal never reaches it and no project-wide handler is
    involved. Plain Django rather than DRF, so it answers JSON whatever the
    request will accept.

    Exempt from CSRF because every DRF view already is, and this stands in for
    them; a plain view does not get that for free. There is nothing to protect:
    the node is read-only and unauthenticated, and this path does not exist.
    Without it, `POST` to an unrouted path answers Django's 403 HTML page.
    """
    return JsonResponse(as_body(InvalidRoute(request.method, request.path)), status=404)
