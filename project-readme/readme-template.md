## Contents 

This download includes single-cell or single-nuclei gene expression files and associated metadata for samples from project [project_accession](project_url) in the ScPCA portal.

- Gene expression files, available as an RDS file containing a `SingleCellExperiment` object, house the expression data, cell and gene metrics, associated metadata, and in the case of multi-modal data like CITE-seq, data from the additional cell-based assays. 
See the [Single-cell gene expression file contents](https://scpca.readthedocs.io/en/latest/sce_file_contents.html) section of the ScPCA Portal Docs for more detailed information on the contents of the gene expression files.

- In the download, there will be a single folder corresponding to each sample, indicated by the `SCPCS` prefix. 
The sample folder will hold two RDS files for each library, indicated by the `SCPCL` prefix, available for that sample. 
These two RDS files correspond to unfiltered and filtered gene expression files.

- Also included in each download is a `libraries_metadata.csv`, a comma-separated table, with one row per library and columns containing pertinent metadata corresponding to that library. 

See the [Downloadable files](https://scpca.readthedocs.io/en/latest/download_files.html) section of the ScPCA Portal Docs for more detailed information on the contents of each download.
   
## Usage

For instructions on using the RDS files see [FAQ: How do I use the provided files in R?](https://scpca.readthedocs.io/en/latest/faq.html#how-do-i-use-the-provided-rds-files-in-r) or [FAQ: What if I want to use Python instead of R?](https://scpca.readthedocs.io/en/latest/faq.html#what-if-i-want-to-use-python-instead-of-r)

## Contact 

If you identify issues with this download, please file an [issue on GitHub.](https://github.com/AlexsLemonade/scpca-portal) If you would prefer to report issues via e-mail, you can also email scpca@ccdatalab.org.

## Citing

To cite data from this project_accession, see the [project_accession page.](project_url)

## Terms and Conditions

By downloading and using the data available in the ScPCA Portal, you agree to our [terms of use.](https://scpca.alexslemonade.org/terms-of-use)
