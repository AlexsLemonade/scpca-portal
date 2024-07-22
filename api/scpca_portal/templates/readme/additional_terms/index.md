{% with heading="### Additional Restrictions" text="This dataset is designated as research or academic purposes only." %}

{% if projects|length > 1 %}

{% with has_additional_restrictions=False %}

{% for project in projects %}
{% if project.additional_restrictions %}
{% with has_additional_restrictions=True %}
{% endwith %}
{% endif %}
{% empty %}
{% endfor %}

{% if has_additional_restrictions %}
{{ heading }}
| Project ID | Data Usage Restrictions |
| :--------- | :---------------------- |
{% for project in projects %}
{% if project.additional_restrictions %}
|[{{ project.scpca_id }}](https://scpca.alexslemonade.org/projects/{{ project.scpca_id }})|{{ project.additional_restrictions }}|
{% endif %}
{% endfor %}
{% endif %}

{% endwith %}

{% elif projects|length == 1 and projects.0.additional_restrictions %}

{{ heading }}
{{ text }}

{% endif %}

{% endwith %}
