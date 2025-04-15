## Contents

{% if projects|length > 1 %}This download includes associated metadata for samples from all projects currently available at time of download in the ScPCA portal.
{% else %}{% for project in projects %}This download includes associated metadata for samples from project [{{ project.scpca_id }}]({{ project.url }}) in the ScPCA portal.{% endfor %}
{% endif %}
The metadata included in this download contains sample, library, and project-related metadata (e.g., age, sex, diagnosis, sequencing unit, etc.) along with any relevant processing metadata (e.g., software versions, filtering methods used, etc.).

See the [Downloadable files](https://scpca.readthedocs.io/en/stable/download_files.html) section in our documentation for more detailed information on files included in the download.
