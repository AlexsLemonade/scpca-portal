## Citation

If you use these data in your research, you must cite:
- The data submitter using language provided as part of the project abstract (as applicable), the publication listed for the project (as applicable), or both.
- The ScPCA Portal using the language below.

For more information, please see [the How to Cite section of our documentation](https://scpca.readthedocs.io/en/stable/citation.html).

### Citing this project

To cite data from a specific project please find the project abstract and publication information on the project page.

{% for project in dataset.projects %}- [{{ project.scpca_id }}]({{ project.url }})
{% endfor %}
### Citing the ScPCA Portal

When citing the ScPCA Portal, please cite the following preprint:

Hawkins A. G., J. A. Shapiro, S. J. Spielman, D. S. Mejia, D. V. Prasad, et al., 2024 The Single-cell Pediatric Cancer Atlas: Data portal and open-source tools for single-cell transcriptomics of pediatric tumors. _bioRxiv._ https://doi.org/10.1101/2024.04.19.590243
