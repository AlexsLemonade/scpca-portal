import React, { useEffect, useState } from 'react'
import { api } from 'api'
import { config } from 'config'
import { allModalities } from 'config/datasets'
import { Box, Text } from 'grommet'
import { Download as DownloadIcon } from 'grommet-icons'
import { useCCDLDatasetDownloadModalContext } from 'hooks/useCCDLDatasetDownloadModalContext'
import { useDataset } from 'hooks/useDataset'
import { useMyDataset } from 'hooks/useMyDataset'
import { useProjectSamplesTable } from 'hooks/useProjectSamplesTable'
import { differenceArray } from 'helpers/differenceArray'
import { getProjectModalities } from 'helpers/getProjectModalities'
import { getReadable } from 'helpers/getReadable'
import { getReadableModality } from 'helpers/getReadableModality'
import { DatasetAddSamplesModal } from 'components/DatasetAddSamplesModal'
import { Icon } from 'components/Icon'
import { Link } from 'components/Link'
import { Loader } from 'components/Loader'
import { Pill } from 'components/Pill'
import { ProjectSamplesTableModalityCell } from 'components/ProjectSamplesTableModalityCell'
import { ProjectSamplesTableModalityHeader } from 'components/ProjectSamplesTableModalityHeader'
import { Table } from 'components/Table'
import { CCDLDatasetDownloadModal } from 'components/CCDLDatasetDownloadModal'
import { WarningAnnDataMultiplexed } from 'components/WarningAnnDataMultiplexed'

export const ProjectSamplesTable = ({ stickies = 3, children }) => {
  const { datasets } = useCCDLDatasetDownloadModalContext()
  const { getDatasetProjectDataSamples } = useDataset()
  const { myDataset, isDatasetDataEmpty, getMyDatasetProjectDataSamples } =
    useMyDataset()
  const {
    project,
    samples: defaultSamples,
    dataset,
    canAdd,
    canRemove,
    allSamples,
    showBulkInfoText,
    showWarningMultiplexed,
    selectedSamples,
    setAllSamples,
    setFilteredSamples,
    selectModalitySamplesByIds
  } = useProjectSamplesTable()

  const [loaded, setLoaded] = useState(false)
  const [samples, setSamples] = useState(defaultSamples) // For all project samples
  const [addedSamples, setAddedSamples] = useState([]) // For samples already added to myDataset
  const [disableAddToDatasetModal, setDisableAddToDatasetModal] =
    useState(false)

  const hasMultiplexedData = project.has_multiplexed_data

  const infoText = showBulkInfoText
    ? 'Bulk RNA-seq data available only when you download the entire project'
    : null
  const text = canRemove ? 'Uncheck to change or remove modality' : null

  const checkBoxCellWidth =
    getProjectModalities(project).length > 1 ? '200px' : '50px'

  const columns = [
    {
      header: (
        <Box width={checkBoxCellWidth}>
          <ProjectSamplesTableModalityHeader />
        </Box>
      ),
      enableSorting: false,
      accessorKey: 'data',
      cell: ({ row }) => (
        <Box width={checkBoxCellWidth}>
          <ProjectSamplesTableModalityCell sample={row.original} />
        </Box>
      )
    },
    {
      header: 'Sample ID',
      accessorKey: 'scpca_id',
      cell: ({ row }) => (
        <Box>
          <Text>{row.original.scpca_id}</Text>
          {row.original.has_multiplexed_data && (
            <Pill
              textSize="small"
              label={getReadable('has_multiplexed_data')}
              bullet={false}
            />
          )}
        </Box>
      )
    },
    {
      header: 'Diagnosis - Subdiagnosis',
      accessorFn: ({ diagnosis, subdiagnosis }) =>
        `${diagnosis} ${subdiagnosis}`,
      cell: ({ row }) => (
        <Box width={{ max: '200px' }} style={{ whiteSpace: 'normal' }}>
          <Text>{row.original.diagnosis}</Text>
          <Text size="small">{row.original.subdiagnosis}</Text>
        </Box>
      )
    },
    { header: 'Disease Timing', accessorKey: 'disease_timing' },
    { header: 'Tissue Location', accessorKey: 'tissue_location' },
    {
      header: 'Treatment',
      accessorFn: ({ treatment }) => treatment || 'N/A'
    },
    {
      header: 'Age',
      accessorKey: 'age'
    },
    {
      header: 'Age Timing',
      accessorKey: 'age_timing'
    },
    { header: 'Sex', accessorKey: 'sex' },
    {
      header: 'Modalities',
      accessorFn: ({ modalities }) =>
        modalities.map(getReadableModality).join(', ')
    },
    {
      header: 'Sequencing Units',
      accessorKey: 'seq_units',
      cell: ({ row }) => <Text>{row.original.seq_units.join(', ')}</Text>
    },
    {
      header: 'Technology',
      accessorKey: 'technologies',
      cell: ({ row }) => <Text>{row.original.technologies.join(', ')}</Text>
    },
    {
      header: 'Multiplexed with',
      accessorKey: 'multiplexed_with',
      cell: ({
        row: {
          original: { multiplexed_with: multiplexedWith }
        }
      }) => (
        <Box width={{ max: '200px' }} style={{ whiteSpace: ' break-spaces' }}>
          {multiplexedWith.length ? multiplexedWith.join(', ') : 'N/A'}
        </Box>
      ),
      isVisible: hasMultiplexedData
    },
    {
      header: 'Sample Count Estimates',
      accessorFn: ({ sample_cell_count_estimate: count }) => count || 'N/A'
    },
    {
      id: 'demux_cell_count_estimate_sum',
      header: () => (
        <Box direction="row" align="center">
          Est. Demux Sample Counts&nbsp;
          <Link href={config.links.what_est_demux_cell}>
            <Icon size="small" name="Help" />
          </Link>
          &nbsp;&nbsp;
        </Box>
      ),
      accessorFn: ({ demux_cell_count_estimate_sum: count }) => count || 'N/A',
      isVisible: hasMultiplexedData
    },
    {
      header: 'Additional Metadata Fields',
      accessorFn: ({ additional_metadata: data }) =>
        Object.keys(data).join(', ')
    }
  ]

  useEffect(() => {
    const asyncFetch = async () => {
      const samplesRequest = await api.samples.list({
        project__scpca_id: project.scpca_id,
        limit: 1000 // TODO:: 'all' option
      })
      if (samplesRequest.isOk) {
        setSamples(samplesRequest.response.results)
        setLoaded(true)
      }
    }
    if (!samples && !loaded) asyncFetch()
    if (samples && !loaded) setLoaded(true)
  }, [samples, loaded])

  // Disable DatasetAddSamplesModal if all samples are added
  useEffect(() => {
    if (samples && loaded) {
      const datasetProjectData = getMyDatasetProjectDataSamples(project)
      const samplesLeft = allModalities
        .map((m) =>
          differenceArray(project.modality_samples[m], datasetProjectData[m])
        )
        .flat()

      setDisableAddToDatasetModal(samplesLeft.length === 0)
    }
  }, [myDataset, samples, loaded])

  // Preselect samples that are already in the dataset
  useEffect(() => {
    if (!allSamples.length || !samples) return

    // Run only when the dataset contains data
    if (!dataset.data && isDatasetDataEmpty) return

    // Use dataset on /datasets, otherwise use myDataset for setup
    const projectData = dataset
      ? getDatasetProjectDataSamples(dataset, project)
      : getMyDatasetProjectDataSamples(project)

    setAddedSamples(projectData)
    selectModalitySamplesByIds('SINGLE_CELL', projectData.SINGLE_CELL)
    selectModalitySamplesByIds('SPATIAL', projectData.SPATIAL)
  }, [dataset, myDataset, allSamples, samples])

  if (!loaded)
    return (
      <Box margin="64px">
        <Loader />
      </Box>
    )

  return (
    <>
      {canAdd && (
        <Box direction="row" justify="end">
          <DatasetAddSamplesModal
            project={project}
            samples={samples}
            disabled={disableAddToDatasetModal}
          />
        </Box>
      )}
      <Table
        columns={columns}
        data={samples}
        filter
        stickies={stickies}
        pageSize={1000}
        pageSizeOptions={[1000]} // Temporary value
        infoText={infoText}
        text={text}
        defaultSort={[{ id: 'scpca_id', asc: true }]}
        prevSelectedRows={addedSamples}
        selectedRows={selectedSamples}
        onAllRowsChange={setAllSamples}
        onFilteredRowsChange={setFilteredSamples}
      >
        {datasets && (
          <Box direction="row" justify="end" pad={{ bottom: 'medium' }}>
            <CCDLDatasetDownloadModal
              label="Download Sample Metadata"
              icon={<DownloadIcon color="brand" />}
            />
          </Box>
        )}
        {/* Only display this warning when myDataset format has already been defined */}
        {showWarningMultiplexed && myDataset.format && (
          <WarningAnnDataMultiplexed />
        )}
      </Table>
      <Box>{children}</Box>
    </>
  )
}
