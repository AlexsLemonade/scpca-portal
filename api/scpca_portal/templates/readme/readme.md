{% with project_accession=projects.0.scpca_id project_url=projects.0.url %}

Generated on: {{ date }}

# Alex's Lemonade Stand Foundation Single-cell Pediatric Cancer Atlas

The [Single-cell Pediatric Cancer Atlas](https://scpca.alexslemonade.org) is a database of single-cell and single-nuclei data from pediatric cancer clinical samples and xenografts, built by the [Childhood Cancer Data Lab](https://www.ccdatalab.org/) at [Alex's Lemonade Stand Foundation](https://www.alexslemonade.org/).

{% include contents_template %}{% include "readme/usage/index.md" %}{% include "readme/changelog/index.md" %}
{% include "readme/contact/index.md" %}
{% include "readme/citation/index.md" %}
{% include "readme/terms_of_use/index.md" %}
{% endwith %}
