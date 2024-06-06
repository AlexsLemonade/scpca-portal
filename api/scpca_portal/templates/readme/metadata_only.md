{% load custom_filters %}
Generated on: {{ date }}

# Alex's Lemonade Stand Foundation Single-cell Pediatric Cancer Atlas

The [Single-cell Pediatric Cancer Atlas](https://scpca.alexslemonade.org) is a database of single-cell and single-nuclei data from pediatric cancer clinical samples and xenografts, built by the [Childhood Cancer Data Lab](https://www.ccdatalab.org/) at [Alex's Lemonade Stand Foundation](https://www.alexslemonade.org/).

## Contents

{% if entire_portal %}
This download includes associated metadata for samples from all projects currently available at time of download in the ScPCA portal.
{% else %}
This download includes associated metadata for samples from project {{ included_projects|markdown_links }} in the ScPCA portal.
{% endif %}

The metadata included in this download contains sample, library, and project-related metadata (e.g., age, sex, diagnosis, sequencing unit, etc.) along with any relevant processing metadata (e.g., software versions, filtering methods used, etc.).

See the [Downloadable files](https://scpca.readthedocs.io/en/stable/download_files.html) section in our documentation for more detailed information on files included in the download.

## CHANGELOG

A summary of changes impacting downloads from the ScPCA Portal is available in [the CHANGELOG section of our documentation](https://scpca.readthedocs.io/en/stable/CHANGELOG.html).

## Contact

If you identify issues with this download, please [file an issue on GitHub.](https://github.com/AlexsLemonade/scpca-portal/issues/new) If you would prefer to report issues via e-mail, please contact us at [scpca@ccdatalab.org](mailto:scpca@ccdatalab.org).

## Citation

If you use these data in your research, you must cite:

- The data submitter using language provided as part of the project abstract (as applicable), the publication listed for the project (as applicable), or both.
- The ScPCA Portal using the language below.

For more information, please see [the How to Cite section of our documentation](https://scpca.readthedocs.io/en/stable/citation.html).

### Citing this project

{% for project_accession, project_url in included_projects %}
To cite data from {{ project_accession }}, please see the project abstract and publication information at [{{ project_accession }} page.]({{ project_url }})
{% endfor %}

### Citing the ScPCA Portal

When citing the ScPCA Portal, please cite the following preprint:

Hawkins A. G., J. A. Shapiro, S. J. Spielman, D. S. Mejia, D. V. Prasad, et al., 2024 The Single-cell Pediatric Cancer Atlas: Data portal and open-source tools for single-cell transcriptomics of pediatric tumors. _bioRxiv._ https://doi.org/10.1101/2024.04.19.590243

## Terms of Use

In using these data, you agree to our [Terms of Use](https://scpca.alexslemonade.org/terms-of-use).

{% if additional_terms %}
{{ additional_terms }}
{% endif %}
