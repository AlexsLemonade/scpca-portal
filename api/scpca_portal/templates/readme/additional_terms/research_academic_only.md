### Additional Restrictions

{% if projects|length > 1 %}
|Project ID|Data Usage Restrictions|
|:---------|:--------------------|
{% for project in projects %}
|[{{ project.scpca_id }}](https://scpca.alexslemonade.org/projects/{{ project.scpca_id }})|{{ project.additional_restrictions }}|
{% endfor %}
{% else %}
This dataset is designated as research or academic purposes only.
{% endif %}
