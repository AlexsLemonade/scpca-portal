import React, { useEffect, useState } from 'react'
import { api } from 'api'
import { config } from 'config'
import { Box, Text } from 'grommet'
import { useMyDataset } from 'hooks/useMyDataset'
import { useProjectSamplesTable } from 'hooks/useProjectSamplesTable'
import { differenceArray } from 'helpers/differenceArray'
import { getReadable } from 'helpers/getReadable'
import { getReadableModality } from 'helpers/getReadableModality'
import { DatasetAddSamplesModal } from 'components/DatasetAddSamplesModal'
import { Icon } from 'components/Icon'
import { Link } from 'components/Link'
import { Loader } from 'components/Loader'
import { ModalityCheckBox } from 'components/ModalityCheckBox'
import { Pill } from 'components/Pill'
import { Table } from 'components/Table'
import { TriStateModalityCheckBoxHeader } from 'components/TriStateModalityCheckBoxHeader'
import { WarningAnnDataMultiplexed } from 'components/WarningAnnDataMultiplexed'

export const ProjectSamplesTable = ({ stickies = 3 }) => {
  const {
    myDataset,
    userFormat,
    getDatasetProjectData,
    getProjectSingleCellSamples,
    getProjectSpatialSamples
  } = useMyDataset()
  const {
    project,
    samples: defaultSamples,
    canAdd,
    canRemove,
    readOnly,
    selectedSamples,
    setAllSamples,
    setFilteredSamples,
    toggleSample
  } = useProjectSamplesTable()

  const [loaded, setLoaded] = useState(false)
  const [samples, setSamples] = useState(defaultSamples)
  const [disableAddToDataset, setDisableAddToDataset] = useState(false)

  const hasMultiplexedData = project.has_multiplexed_data
  const showWarningMultiplexed =
    hasMultiplexedData && (myDataset.forat || userFormat) === 'ANN_DATA'

  const infoText =
    canAdd && project && project.has_bulk_rna_seq
      ? 'Bulk RNA-seq data available only when you download the entire project'
      : null

  const text = canRemove ? 'Uncheck to change or remove modality' : null

  const allModalities = ['SINGLE_CELL', 'SPATIAL'] // List of all modalities available on the portal
  const availableModalities = [
    { key: 'SINGLE_CELL', value: project.has_single_cell_data },
    { key: 'SPATIAL', value: project.has_spatial_data }
  ]
    .filter((m) => m.value)
    .map((m) => m.key)

  const checkBoxCellWidth = availableModalities.length > 1 ? '200px' : '50px'

  const columns = [
    {
      Header: (
        <Box width={checkBoxCellWidth}>
          <TriStateModalityCheckBoxHeader
            project={project}
            modalities={availableModalities}
            readOnly={readOnly}
            partialToggle={canAdd}
          />
        </Box>
      ),
      disableSortBy: true,
      accessor: 'data',
      Cell: ({ row }) => (
        <Box
          align="center"
          direction="row"
          justify="around"
          width={checkBoxCellWidth}
        >
          {availableModalities.map((m) => (
            <ModalityCheckBox
              key={`${row.original.scpca_id}_${m}`}
              project={project}
              modality={m}
              samples={samples}
              sample={row.original}
              readOnly={readOnly}
              partialToggle={canAdd}
              onClick={() => toggleSample(m, row.original)}
            />
          ))}
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
      Header: 'Modalities',
      accessor: ({ modalities }) =>
        modalities.map(getReadableModality).join(', ')
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

  useEffect(() => {
    if (samples && loaded) {
      const datasetData = getDatasetProjectData(project)

      const projectSamplesByModality = {
        SINGLE_CELL: getProjectSingleCellSamples(samples),
        SPATIAL: getProjectSpatialSamples(samples)
      }

      const datasetSamplesByModality = {
        SINGLE_CELL:
          datasetData.SINGLE_CELL === 'MERGED'
            ? projectSamplesByModality.SINGLE_CELL
            : datasetData.SINGLE_CELL || [],
        SPATIAL: datasetData.SPATIAL || []
      }

      const samplesLeft = allModalities
        .map((m) =>
          differenceArray(
            projectSamplesByModality[m],
            datasetSamplesByModality[m] || []
          )
        )
        .flat()

      setDisableAddToDataset(samplesLeft.length === 0)
    }
  }, [myDataset, samples, loaded])

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
            disabled={disableAddToDataset}
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
        selectedRows={selectedSamples}
        onAllRowsChange={setAllSamples}
        onFilteredRowsChange={setFilteredSamples}
      >
        {canAdd && showWarningMultiplexed && <WarningAnnDataMultiplexed />}
      </Table>
    </>
  )
}
