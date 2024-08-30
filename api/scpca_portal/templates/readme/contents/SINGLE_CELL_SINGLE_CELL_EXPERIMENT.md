## Contents

This download includes single-cell or single-nuclei gene expression files and associated metadata for samples from project [{{ project_accession }}]({{ project_url }}) in the ScPCA portal.

Each sample folder (indicated by the `SCPCS` prefix) contains the files for all libraries (`SCPCL` prefix) derived from that biological sample.
Most samples only have one library that has been sequenced.
See the [FAQ section about samples and libraries](https://scpca.readthedocs.io/en/stable/faq.html#what-is-the-difference-between-samples-and-libraries) for more information.

The files associated with each library are (example shown for a library with ID `SCPCL000000`):

- An unfiltered counts file: `SCPCL000000_unfiltered.rds`,
- A filtered counts file: `SCPCL000000_filtered.rds`,
- A processed counts file: `SCPCL000000_processed.rds`,
- A quality control report: `SCPCL000000_qc.html`,
- A supplemental cell type report: `SCPCL000000_celltype-report.html`

Also included in each download is `single_cell_metadata.tsv`, a tab-separated table, with one row per library and columns containing pertinent metadata corresponding to that library.

Gene expression files, available as RDS files containing a `SingleCellExperiment` object, house the expression data, cell and gene metrics, associated metadata, and in the case of multi-modal data like CITE-seq, data from the additional cell-based assays (see [Single-cell gene expression file contents](https://scpca.readthedocs.io/en/stable/sce_file_contents.html) for more information).

This download does not include any samples that are part of multiplexed libraries.
To download all samples in this project, including multiplexed libraries, if present, visit the [project page]({{project_url}}).

If a project contains bulk RNA-seq data, two tab-separated value files, `bulk_quant.tsv` and `bulk_metadata.tsv`, will be included in the download.
The `bulk_quant.tsv` file contains a gene by sample matrix (each row a gene, each column a sample) containing raw gene expression counts quantified by Salmon.
The `bulk_metadata.tsv` file contains associated metadata for all samples with bulk RNA-seq data.

See the [Downloadable files](https://scpca.readthedocs.io/en/stable/download_files.html) section in our documentation for more detailed information on files included in the download.
