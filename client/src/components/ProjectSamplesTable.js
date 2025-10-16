import React, { useEffect, useState } from 'react'
import { api } from 'api'
import { config } from 'config'
import { Box, Text } from 'grommet'
import { useMyDataset } from 'hooks/useMyDataset'
import { useDatasetSamplesTable } from 'hooks/useDatasetSamplesTable'
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
import { TriStateModalityCheckBox } from 'components/TriStateModalityCheckBox'
import { WarningAnnDataMultiplexed } from 'components/WarningAnnDataMultiplexed'

export const ProjectSamplesTable = ({
  project,
  samples: defaultSamples,
  stickies = 3
}) => {
  const {
    myDataset,
    userFormat,
    getDatasetProjectData,
    getProjectSingleCellSamples,
    getProjectSpatialSamples
  } = useMyDataset()
  const { selectedSamples, setAllSamples, setFilteredSamples, toggleSample } =
    useDatasetSamplesTable()

  const [loaded, setLoaded] = useState(false)
  const [samples, setSamples] = useState(defaultSamples)
  const [disableAddToDataset, setDisableAddToDataset] = useState(false)

  const hasMultiplexedData = project.has_multiplexed_data
  const showWarningMultiplexed =
    hasMultiplexedData && (myDataset.forat || userFormat) === 'ANN_DATA'

  const infoText =
    project && project.has_bulk_rna_seq
      ? 'Bulk RNA-seq data available only when you download the entire project'
      : false

  const allModalities = ['SINGLE_CELL', 'SPATIAL'] // List of all modalities available on the portal
  const checkBoxCellWidth = '200px'

  const columns = [
    {
      Header: (
        <Box width={checkBoxCellWidth}>
          <Box align="center" margin={{ bottom: 'small' }} pad="small">
            Select Modality
          </Box>
          <Box
            border={{ side: 'bottom' }}
            width="100%"
            style={{ position: 'absolute', top: '45px', left: 0 }}
          />
          <Box direction="row" justify="around">
            {allModalities.map((m) => (
              <Box key={m} align="center" pad={{ horizontal: 'small' }}>
                <Text margin={{ bottom: 'xsmall' }}>{getReadable(m)}</Text>
                <TriStateModalityCheckBox
                  project={project}
                  modality={m}
                  disabled={!project[`has_${m.toLowerCase()}_data`]}
                  partialToggle
                />
              </Box>
            ))}
          </Box>
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
          {allModalities.map((m) => (
            <ModalityCheckBox
              key={`${row.original.scpca_id}_${m}`}
              project={project}
              modality={m}
              samples={samples}
              sampleId={row.original.scpca_id}
              disabled={!row.original[`has_${m.toLowerCase()}_data`]}
              partialToggle
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
      <Box direction="row" justify="end">
        <DatasetAddSamplesModal
          project={project}
          samples={samples}
          disabled={disableAddToDataset}
        />
      </Box>
      <Table
        columns={columns}
        data={samples}
        filter
        stickies={stickies}
        pageSize={5}
        pageSizeOptions={[5, 10, 20, 50]}
        infoText={infoText}
        defaultSort={[{ id: 'scpca_id', asc: true }]}
        selectedRows={selectedSamples}
        onAllRowsChange={setAllSamples}
        onFilteredRowsChange={setFilteredSamples}
      >
        {showWarningMultiplexed && <WarningAnnDataMultiplexed />}
      </Table>
    </>
  )
}
