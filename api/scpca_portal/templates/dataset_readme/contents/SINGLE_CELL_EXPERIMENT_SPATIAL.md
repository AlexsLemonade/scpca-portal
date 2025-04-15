## Contents

This download includes gene expression data from libraries processed using spatial transcriptomics and associated metadata for samples from project [{{ project_accession }}]({{ project_url }}) in the ScPCA portal.

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
