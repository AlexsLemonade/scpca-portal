## Contents

This download includes single-cell or single-nuclei gene expression files and associated metadata for samples from project [{{ project_accession }}]({{ project_url }}) in the ScPCA portal.

This project includes multiplexed samples, where multiple biological samples have been combined into libraries using cellhashing or similar technologies.
The data files are divided into folders named with an underscore-separated list of the sample ids (each with an `SCPCS` prefix) for each set of multiplexed samples.
Each of these folders contains the files for all libraries (`SCPCL` prefix) derived from that set of samples.
See the FAQ sections about [samples and libraries](https://scpca.readthedocs.io/en/stable/faq.html#what-is-the-difference-between-samples-and-libraries) and [multiplexed samples](https://scpca.readthedocs.io/en/stable/faq.html#what-is-a-multiplexed-sample) for more information.

The files associated with each library are (example shown for a library with ID `SCPCL000000`):

- An unfiltered counts file: `SCPCL000000_unfiltered.rds`,
- A filtered counts file: `SCPCL000000_filtered.rds`,
- A processed counts file: `SCPCL000000_processed.rds`,
- A quality control report: `SCPCL000000_qc.html`,

Also included in each download is a `single_cell_metadata.tsv`, a tab-separated table, with one row per sample/library pair and columns containing pertinent metadata corresponding to that sample and library.

Gene expression files, available as RDS files containing a `SingleCellExperiment` object, house the expression data, cell and gene metrics, associated metadata, and, in the case of multiplexed samples, data from the the cellhash assay (see [Single-cell gene expression file contents](https://scpca.readthedocs.io/en/stable/sce_file_contents.html) for more information).
Please note that the libraries derived from multiplexed samples are _not demultiplexed_, however, [results from demultiplexing algorithms](https://scpca.readthedocs.io/en/stable/sce_file_contents.html#additional-singlecellexperiment-components-for-multiplexed-libraries) are included in the `_filtered.rds` files.

If a project contains bulk RNA-seq data, two tab-separated value files, `bulk_quant.tsv` and `bulk_metadata.tsv`, will be included in the download.
The `bulk_quant.tsv` file contains a gene by sample matrix (each row a gene, each column a sample) containing raw gene expression counts quantified by Salmon.
The `bulk_metadata.tsv` file contains associated metadata for all samples with bulk RNA-seq data.

See the [Downloadable files](https://scpca.readthedocs.io/en/stable/download_files.html) section in our documentation for more detailed information on files included in the download.
