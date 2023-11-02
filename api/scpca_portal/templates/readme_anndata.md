Generated on: {date}

# Alex's Lemonade Stand Foundation Single-cell Pediatric Cancer Atlas

The [Single-cell Pediatric Cancer Atlas](https://scpca.alexslemonade.org) is a database of single-cell and single-nuclei data from pediatric cancer clinical samples and xenografts, built by the [Childhood Cancer Data Lab](https://www.ccdatalab.org/) at [Alex's Lemonade Stand Foundation](https://www.alexslemonade.org/).

## Contents

This download includes single-cell or single-nuclei gene expression files and associated metadata for samples from project [{project_accession}]({project_url}) in the ScPCA portal.

Each sample folder (indicated by the `SCPCS` prefix) contains the files for all libraries (`SCPCL` prefix) derived from that biological sample.
Most samples only have one library that has been sequenced.
See the [FAQ section about samples and libraries](https://scpca.readthedocs.io/en/stable/faq.html#what-is-the-difference-between-samples-and-libraries) for more information.

The files associated with each library are (example shown for a library with ID `SCPCL000000`):
- An unfiltered counts file: `SCPCL000000_unfiltered_rna.hdf5`,
- A filtered counts file: `SCPCL000000_filtered_rna.hdf5`,
- A processed counts file: `SCPCL000000_processed_rna.hdf5`,
- A quality control report: `SCPCL000000_qc.html`

Also included in each download is `single_cell_metadata.tsv`, a tab-separated table, with one row per library and columns containing pertinent metadata corresponding to that library.

Gene expression files, available as HDF5 files containing an `AnnData` object, house the expression data, cell and gene metrics, and associated metadata (see [Single-cell gene expression file contents](https://scpca.readthedocs.io/en/stable/sce_file_contents.html) for more information).

In the case of multi-modal data like CITE-seq (ADT tags), the ADT expression matrices will be provided in separate files corresponding to the same three stages of data processing: an unfiltered object (`_unfiltered_adt.hdf5`), a filtered object (`_filtered_adt.hdf5`), and a processed object (`_processed_adt.hdf5`).
These files will only contain ADT expression data and not RNA expression data.

If a project contains bulk RNA-seq data, two tab-separated value files, `bulk_quant.tsv` and `bulk_metadata.tsv`, will be included in the download.
The `bulk_quant.tsv` file contains a gene by sample matrix (each row a gene, each column a sample) containing raw gene expression counts quantified by Salmon.
The `bulk_metadata.tsv` file contains associated metadata for all samples with bulk RNA-seq data.

See the [Downloadable files](https://scpca.readthedocs.io/en/stable/download_files.html) section in our documentation for more detailed information on files included in the download.

## Usage

For instructions on using the HDF5 files, please see [FAQ: How do I use the provided HDF5 files in Python?](https://scpca.readthedocs.io/en/stable/faq.html#how-do-i-use-the-provided-HDF5-files-in-python)
For more information on working with the processed `AnnData` objects, see [`Getting started with an ScPCA dataset`](https://scpca.readthedocs.io/en/stable/getting_started.html).

## Contact

If you identify issues with this download, please [file an issue on GitHub.](https://github.com/AlexsLemonade/scpca-portal/issues/new) If you would prefer to report issues via e-mail, please contact us at [scpca@ccdatalab.org](mailto:scpca@ccdatalab.org).

## Citing

To cite data from {project_accession}, please see the citation information at [{project_accession} page]({project_url}).

## Terms of Use

In using these data, you agree to our [Terms of Use](https://scpca.alexslemonade.org/terms-of-use).