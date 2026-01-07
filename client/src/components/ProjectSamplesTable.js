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

export const ProjectSamplesTable = ({ stickies = 3 }) => {
  const { datasets } = useCCDLDatasetDownloadModalContext()
  const { getDatasetProjectData } = useDataset()
  const {
    myDataset,
    getDatasetProjectDataSamples,
    getProjectSingleCellSamples,
    getProjectSpatialSamples
  } = useMyDataset()
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
      Header: (
        <Box width={checkBoxCellWidth}>
          <ProjectSamplesTableModalityHeader />
        </Box>
      ),
      disableSortBy: true,
      accessor: 'data',
      Cell: ({ row }) => (
        <Box width={checkBoxCellWidth}>
          <ProjectSamplesTableModalityCell sample={row.original} />
        </Box>
      )
    },
    {
      Header: 'Sample ID',
      accessor: 'scpca_id',
      Cell: ({ row }) => (
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
      Header: 'Diagnosis - Subdiagnosis',
      accessor: ({ diagnosis, subdiagnosis }) => `${diagnosis} ${subdiagnosis}`,
      Cell: ({ row }) => (
        <Box width={{ max: '200px' }} style={{ whiteSpace: 'normal' }}>
          <Text>{row.original.diagnosis}</Text>
          <Text size="small">{row.original.subdiagnosis}</Text>
        </Box>
      )
    },
    { Header: 'Disease Timing', accessor: 'disease_timing' },
    { Header: 'Tissue Location', accessor: 'tissue_location' },
    {
      Header: 'Treatment',
      accessor: ({ treatment }) => treatment || 'N/A'
    },
    {
      Header: 'Age',
      accessor: 'age'
    },
    {
      Header: 'Age Timing',
      accessor: 'age_timing'
    },
    { Header: 'Sex', accessor: 'sex' },
    {
      Header: 'Modalities',
      accessor: ({ modalities }) =>
        modalities.map(getReadableModality).join(', ')
    },
    {
      Header: 'Sequencing Units',
      accessor: 'seq_units',
      Cell: ({ row }) => <Text>{row.original.seq_units.join(', ')}</Text>
    },
    {
      Header: 'Technology',
      accessor: 'technologies',
      Cell: ({ row }) => <Text>{row.original.technologies.join(', ')}</Text>
    },
    {
      Header: 'Multiplexed with',
      accessor: 'multiplexed_with',
      Cell: ({
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
      Header: 'Sample Count Estimates',
      accessor: ({ sample_cell_count_estimate: count }) => count || 'N/A'
    },
    {
      id: 'demux_cell_count_estimate_sum',
      Header: () => (
        <Box direction="row" align="center">
          Est. Demux Sample Counts&nbsp;
          <Link href={config.links.what_est_demux_cell}>
            <Icon size="small" name="Help" />
          </Link>
          &nbsp;&nbsp;
        </Box>
      ),
      accessor: ({ demux_cell_count_estimate_sum: count }) => count || 'N/A',
      isVisible: hasMultiplexedData
    },
    {
      Header: 'Additional Metadata Fields',
      accessor: ({ additional_metadata: data }) => Object.keys(data).join(', ')
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
      const projectSamplesByModality = {
        SINGLE_CELL: getProjectSingleCellSamples(samples),
        SPATIAL: getProjectSpatialSamples(samples)
      }

      const datasetProjectData = getDatasetProjectDataSamples(project, samples)

      const samplesLeft = allModalities
        .map((m) =>
          differenceArray(projectSamplesByModality[m], datasetProjectData[m])
        )
        .flat()

      setDisableAddToDatasetModal(samplesLeft.length === 0)
    }
  }, [myDataset, samples, loaded])

  // Preselect samples that are already in the dataset
  useEffect(() => {
    if (!allSamples.length || !samples) return

    let projectData

    if (dataset?.data) {
      projectData = getDatasetProjectData(dataset, project)
    } else if (!dataset && myDataset?.data) {
      projectData = getDatasetProjectDataSamples(project, samples)
    } else {
      return
    }

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
        pageSize={5}
        pageSizeOptions={[5, 10, 20, 50]}
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
    </>
  )
}
