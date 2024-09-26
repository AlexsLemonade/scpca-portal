## Contents

This download includes single-cell or single-nuclei gene expression data and associated metadata for all samples and libraries from a project [{{ project_accession }}]({{ project_url }}) in the ScPCA portal.
All gene expression data for all samples and libraries have been merged into a single `SingleCellExperiment` object, stored as an `.rds` file.
In addition to the merged object, each download includes a summary report describing the contents of the merged file and a folder with all quality control reports, and, if applicable, cell type annotation reports, for each library included in the merged object.

The download will include the following files for the selected project (example shown for project with ID `SCPCP000000`):

- A merged file containing all gene expression data: `SCPCP000000_merged.rds`
- A summary report: `SCPCP000000_merged-summary-report.html`
- A folder containing all reports for individual libraries:
  - A quality control report: `SCPCL000000_qc.html`
  - A supplemental cell type report: `SCPCL000000_celltype-report.html`

Also included in each download is `single_cell_metadata.tsv`, a tab-separated table, with one row per library and columns containing pertinent metadata corresponding to that library.

Merged objects, available as RDS files containing a `SingleCellExperiment` object, house the expression data, cell and gene metrics, associated metadata, and in the case of multi-modal data like CITE-seq, data from the additional cell-based assays for all samples and libraries from the selected project (see [Merged objects](https://scpca.readthedocs.io/en/stable/merged_objects.html) for more information).

If a project contains bulk RNA-seq data, two tab-separated value files, `bulk_quant.tsv` and `bulk_metadata.tsv`, will be included in the download.
The `bulk_quant.tsv` file contains a gene by sample matrix (each row a gene, each column a sample) containing raw gene expression counts quantified by Salmon.
The `bulk_metadata.tsv` file contains associated metadata for all samples with bulk RNA-seq data.

See the [Downloadable files](https://scpca.readthedocs.io/en/stable/download_files.html) section in our documentation for more detailed information on files included in the download.
