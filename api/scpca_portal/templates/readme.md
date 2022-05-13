# Alex's Lemonade Stand Foundation Single-cell Pediatric Cancer Atlas

The [Single-cell Pediatric Cancer Atlas](https://scpca.alexslemonade.org) is a database of single-cell and single-nuclei data from pediatric cancer clinical samples and xenografts, built by the [Childhood Cancer Data Lab](https://www.ccdatalab.org/) at [Alex's Lemonade Stand Foundation](https://www.alexslemonade.org/).

## Contents

This download includes single-cell or single-nuclei gene expression files and associated metadata for samples from project [{project_accession}]({project_url}) in the ScPCA portal.

Each sample folder (indicated by the `SCPCS` prefix) contains the files for all libraries (`SCPCL` prefix) derived from that biological sample.
Most samples only have one library that has been sequenced.
See the [FAQ section about samples and libraries](https://scpca.readthedocs.io/en/latest/faq.html#what-is-the-difference-between-samples-and-libraries) for more information.

The files associated with each library are (example shown for a library with ID `SCPCL000000`):
- An unfiltered counts file: `SCPCL000000_unfiltered.rds`,
- A filtered counts file: `SCPCL000000_filtered.rds`,
- A quality control report: `SCPCL000000_qc.html`

Also included in each download is a `single_cell_metadata.tsv`, a comma-separated table, with one row per library and columns containing pertinent metadata corresponding to that library.

Gene expression files, available as RDS files containing a `SingleCellExperiment` object, house the expression data, cell and gene metrics, associated metadata, and in the case of multi-modal data like CITE-seq, data from the additional cell-based assays (see [Single-cell gene expression file contents](https://scpca.readthedocs.io/en/latest/sce_file_contents.html) for more information).

If a project contains bulk RNA-seq data, two tab-separated value files, `bulk_quant.tsv` and `bulk_metadata.tsv`, will be included in the download.
The `bulk_quant.tsv` file contains a gene by sample matrix (each row a gene, each column a sample) containing raw gene expression counts quantified by Salmon.
The `bulk_metadata.tsv` file contains associated metadata for all samples with bulk RNA-seq data.

See the [Downloadable files](https://scpca.readthedocs.io/en/latest/download_files.html) section in our documentation for more detailed information on files included in the download.

## Usage

For instructions on using the RDS files, please see [FAQ: How do I use the provided files in R?](https://scpca.readthedocs.io/en/latest/faq.html#how-do-i-use-the-provided-rds-files-in-r) or [FAQ: What if I want to use Python instead of R?](https://scpca.readthedocs.io/en/latest/faq.html#what-if-i-want-to-use-python-instead-of-r)

## Contact

If you identify issues with this download, please [file an issue on GitHub.](https://github.com/AlexsLemonade/scpca-portal/issues/new) If you would prefer to report issues via e-mail, please contact us at [scpca@ccdatalab.org](mailto:scpca@ccdatalab.org).

## Citing

To cite data from {project_accession}, please see the citation information at [{project_accession} page.]({project_url})

## Terms of Use

In using these data, you agree to our [Terms of Use.](https://scpca.alexslemonade.org/terms-of-use)
