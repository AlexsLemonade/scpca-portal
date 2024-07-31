### Additional Restrictions
|Project ID|Data Usage Restrictions|
|:---------|:----------------------|
{% for project in projects %}|[{{ project.scpca_id }}]({{ project.url }}) | {{ project.additional_restrictions|default:"No additional restrictions" }}|{% endfor %}
