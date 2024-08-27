Generated on: TEST_TODAYS_DATE

# Alex's Lemonade Stand Foundation Single-cell Pediatric Cancer Atlas

The [Single-cell Pediatric Cancer Atlas](https://scpca.alexslemonade.org) is a database of single-cell and single-nuclei data from pediatric cancer clinical samples and xenografts, built by the [Childhood Cancer Data Lab](https://www.ccdatalab.org/) at [Alex's Lemonade Stand Foundation](https://www.alexslemonade.org/).

## Contents

This download includes gene expression data from libraries processed using spatial transcriptomics and associated metadata for samples from project [PROJECT_ID_0](https://scpca.alexslemonade.org/projects/PROJECT_ID_0) in the ScPCA portal.

For all spatial transcriptomics libraries (indicated by the `SCPCL` prefix) , a `SCPCL000000_spatial` folder will be nested inside the corresponding sample folder (`SCPCS` prefix) in the download.
See the [FAQ section about samples and libraries](https://scpca.readthedocs.io/en/stable/faq.html#what-is-the-difference-between-samples-and-libraries) for more information.

Inside the `SCPCL000000_spatial` folder will be the following folders and files:

- A `raw_feature_bc_matrix` folder containing the [unfiltered counts files](https://support.10xgenomics.com/spatial-gene-expression/software/pipelines/latest/output/matrices)
- A `filtered_feature_bc_matrix` folder containing the [filtered counts files](https://support.10xgenomics.com/spatial-gene-expression/software/pipelines/latest/output/matrices)
- A `spatial` folder containing [images and position information](https://support.10xgenomics.com/spatial-gene-expression/software/pipelines/latest/output/images)
- A `SCPCL000000_spaceranger_summary.html` file containing the [summary html report provided by Space Ranger](https://support.10xgenomics.com/spatial-gene-expression/software/pipelines/latest/output/summary)
- A `SCPCL000000_metadata.json` file containing library processing information.

Also included in each download is a `spatial_metadata.tsv`, a tab separated values table, with one row per library and columns containing pertinent metadata corresponding to that library.

See the [Downloadable files](https://scpca.readthedocs.io/en/stable/download_files.html#spatial-transcriptomics-libraries) section in our documentation for more detailed information on files included in the download for spatial transcriptomics libraries.

For more information on how the spatial libraries were processed, see the [Spatial Transcriptomics section in the Processing information](https://scpca.readthedocs.io/en/stable/processing_information.html#spatial-transcriptomics) page of the ScPCA Portal documentation.

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

To cite data from PROJECT_ID_0, please see the project abstract and publication information at [PROJECT_ID_0 page.](https://scpca.alexslemonade.org/projects/PROJECT_ID_0)

### Citing the ScPCA Portal

When citing the ScPCA Portal, please cite the following preprint:

Hawkins A. G., J. A. Shapiro, S. J. Spielman, D. S. Mejia, D. V. Prasad, et al., 2024 The Single-cell Pediatric Cancer Atlas: Data portal and open-source tools for single-cell transcriptomics of pediatric tumors. _bioRxiv._ https://doi.org/10.1101/2024.04.19.590243

## Terms of Use

In using these data, you agree to our [Terms of Use](https://scpca.alexslemonade.org/terms-of-use).

### Additional Restrictions

This dataset is designated as research or academic purposes only.
