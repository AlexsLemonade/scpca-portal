# Alex's Lemonade Stand Foundation Single-cell Pediatric Cancer Atlas

The [Single-cell Pediatric Cancer Atlas](https://scpca.alexslemonade.org) is a database of single-cell and single-nuclei data from pediatric cancer clinical samples and xenografts, built by the [Childhood Cancer Data Lab](https://www.ccdatalab.org/) at [Alex's Lemonade Stand Foundation](https://www.alexslemonade.org/).

## Contents

This download includes gene expression data from libraries processed using spatial transcriptomics and associated metadata for samples from project [{project_accession}]({project_url}) in the ScPCA portal.

For all spatial transcriptomics libraries (indicated by the `SCPCL` prefix) , a `SCPCL000000_spatial` folder will be nested inside the corresponding sample folder (`SCPCS` prefix) in the download.
See the [FAQ section about samples and libraries](https://scpca.readthedocs.io/en/latest/faq.html#what-is-the-difference-between-samples-and-libraries) for more information.

Inside the `SCPCL000000_spatial` folder will be the following folders and files:

- A `raw_feature_bc_matrix` folder containing the [unfiltered counts files](https://support.10xgenomics.com/spatial-gene-expression/software/pipelines/latest/output/matrices)
- A `filtered_feature_bc_matrix` folder containing the [filtered counts files](https://support.10xgenomics.com/spatial-gene-expression/software/pipelines/latest/output/matrices)
- A `spatial` folder containing [images and position information](https://support.10xgenomics.com/spatial-gene-expression/software/pipelines/latest/output/images)
- A `SCPCL000000_spaceranger_summary.html` file containing the [summary html report provided by Space Ranger](https://support.10xgenomics.com/spatial-gene-expression/software/pipelines/latest/output/summary)
- A `SCPCL000000_metadata.json` file containing library processing information.

Also included in each download is a `spatial_metadata.tsv`, a tab separated values table, with one row per library and columns containing pertinent metadata corresponding to that library.

See the [Downloadable files](https://scpca.readthedocs.io/en/latest/download_files.html#spatial-transcriptomics-libraries) section in our documentation for more detailed information on files included in the download for spatial transcriptomics libraries.

For more information on how the spatial libraries were processed, see the [Spatial Transcriptomics section in the Processing information](https://scpca.readthedocs.io/en/latest/processing_information.html#spatial-transcriptomics) page of the ScPCA Portal documentation.

## Contact

If you identify issues with this download, please [file an issue on GitHub.](https://github.com/AlexsLemonade/scpca-portal/issues/new) If you would prefer to report issues via e-mail, please contact us at [scpca@ccdatalab.org](mailto:scpca@ccdatalab.org).

## Citing

To cite data from {project_accession}, please see the citation information at [{project_accession} page.]({project_url})

## Terms of Use

In using these data, you agree to our [Terms of Use.](https://scpca.alexslemonade.org/terms-of-use)
