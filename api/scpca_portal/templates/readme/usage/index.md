
{% if download_config.modality == 'SINGLE_CELL' %}
## Usage
{% if download_config.format == 'ANN_DATA' %}For instructions on using the H5AD files, please see [FAQ: How do I use the provided H5AD files in Python?](https://scpca.readthedocs.io/en/stable/faq.html#how-do-i-use-the-provided-h5ad-files-in-python).
For more information on working with the processed `AnnData` objects, see [`Getting started with an ScPCA dataset`](https://scpca.readthedocs.io/en/stable/getting_started.html).

{% elif download_config.excludes_multiplexed %}For instructions on using the RDS files, please see [FAQ: How do I use the provided files in R?](https://scpca.readthedocs.io/en/stable/faq.html#how-do-i-use-the-provided-rds-files-in-r).
For more information on working with the processed `SingleCellExperiment` objects, see [`Getting started with an ScPCA dataset`](https://scpca.readthedocs.io/en/stable/getting_started.html).

{% else %}For instructions on using the RDS files, please see [FAQ: How do I use the provided files in R?](https://scpca.readthedocs.io/en/stable/faq.html#how-do-i-use-the-provided-rds-files-in-r).

For information on how to use the demultiplexing results that the filtered data files contain, see the ["Getting started" section about multiplex samples](https://scpca.readthedocs.io/en/stable/getting_started.html#special-considerations-for-multiplexed-samples).
{% endif %}
{% endif %}
 s