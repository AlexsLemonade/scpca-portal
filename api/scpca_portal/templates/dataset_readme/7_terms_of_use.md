## Terms of Use

In using these data, you agree to our [Terms of Use](https://scpca.alexslemonade.org/terms-of-use).

### Additional Restrictions

|Project ID|Data Usage Restrictions|
|:---------|:----------------------|
{% for project in dataset.projects %}|[{{ project.scpca_id }}]({{ project.url }})|{{ project.additional_restrictions|default:"No additional restrictions" }}|
{% endfor %}
