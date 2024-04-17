Generated on: {date}

# Alex's Lemonade Stand Foundation Single-cell Pediatric Cancer Atlas

The [Single-cell Pediatric Cancer Atlas](https://scpca.alexslemonade.org) is a database of single-cell and single-nuclei data from pediatric cancer clinical samples and xenografts, built by the [Childhood Cancer Data Lab](https://www.ccdatalab.org/) at [Alex's Lemonade Stand Foundation](https://www.alexslemonade.org/).

## Contents

This download includes single-cell or single-nuclei gene expression data and associated metadata for all samples and libraries from a project [{project_accession}]({project_url}) in the ScPCA portal.
All gene expression data for all samples and libraries have been merged into a single `AnnData` object, stored as an `.hdf5` file.
In addition to the merged object, each download includes a summary report describing the contents of the merged file and a folder with all quality control reports, and, if applicable, cell type annotation reports, for each library included in the merged object.

The download will include the following files for the selected project (example shown for project with ID `SCPCP000000`):

- A merged file containing all gene expression data: `SCPCP000000_merged_rna.hdf5`
- A summary report: `SCPCP000000_merged-summary-report.html`
- A folder containing all reports for individual libraries:
  - A quality control report: `SCPCL000000_qc.html`
  - A supplemental cell type report: `SCPCL000000_celltype-report.html`

Also included in each download is `single_cell_metadata.tsv`, a tab-separated table, with one row per library and columns containing pertinent metadata corresponding to that library.

Merged objects, available as HDF5 files containing a `AnnData` object, house the expression data, cell and gene metrics, associated metadata for all samples and libraries from the selected project (see [Merged objects](https://scpca.readthedocs.io/en/stable/merged_objects.html) for more information).

In the case of multi-modal data like CITE-seq (ADT tags), the merged ADT expression matrix will be provided in a separate file, `_merged_adt.hdf5`.
This file will only contain ADT expression data and not RNA expression data.

If a project contains bulk RNA-seq data, two tab-separated value files, `bulk_quant.tsv` and `bulk_metadata.tsv`, will be included in the download.
The `bulk_quant.tsv` file contains a gene by sample matrix (each row a gene, each column a sample) containing raw gene expression counts quantified by Salmon.
The `bulk_metadata.tsv` file contains associated metadata for all samples with bulk RNA-seq data.

See the [Downloadable files](https://scpca.readthedocs.io/en/stable/download_files.html) section in our documentation for more detailed information on files included in the download.

## Usage

For instructions on using the HDF5 files, please see [FAQ: How do I use the provided HDF5 files in Python?](https://scpca.readthedocs.io/en/stable/faq.html#how-do-i-use-the-provided-HDF5-files-in-python)
For more information on working with the processed `AnnData` objects, see [`Getting started with an ScPCA dataset`](https://scpca.readthedocs.io/en/stable/getting_started.html).

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

To cite data from {project_accession}, please see the project abstract and publication information at [{project_accession} page.]({project_url})

### Citing the ScPCA Portal

The date you accessed and downloaded this data is included in the name of the top-most directory of your download for your convenience.
Use this date to populate the access date below.

#### APA Format

Alex's Lemonade Stand Foundation Childhood Cancer Data Lab. (n.d.). The Single-cell Pediatric Cancer Atlas Portal. Retrieved (insert access date), from https://scpca.alexslemonade.org/

#### MLA Format

The Single-cell Pediatric Cancer Atlas Portal, Alex’s Lemonade Stand Foundation Childhood Cancer Data Lab, https://scpca.alexslemonade.org/. Accessed (insert access date).


## Terms of Use

In using these data, you agree to our [Terms of Use](https://scpca.alexslemonade.org/terms-of-use).