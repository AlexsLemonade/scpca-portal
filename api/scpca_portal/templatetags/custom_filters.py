from django import template

register = template.Library()


@register.filter
def markdown_links(included_projects):
    return ", ".join(
        [
            f"[{project_accession}]({project_url})"
            for project_accession, project_url in included_projects
        ]
    )
