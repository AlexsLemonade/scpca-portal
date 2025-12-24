## Contents
{% if content_portal_wide_link %}
This is a portal-wide download you can find more information about your download [in ScPCA docs.]({{ content_portal_wide_link }})
{% endif %}
{% if content_metadata_link %}
This download only contains metadata for your selected projects.
More information can be found [in the ScPCA docs.]({{content_metadata_link}}).
{% endif %}
{% if content_table_rows %}
|Project ID|Modality|Format|Link to Documentation|
|:---------|:-------|:-----|:--------------------|
{% for row in content_table_rows %}|[{{ row.project.scpca_id }}]({{ row.project.url }})|{{ row.modality }}|{{ row.format }}|{{ row.docs }}|
{% endfor %}
{% endif %}
