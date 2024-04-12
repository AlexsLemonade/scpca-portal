import React, { useEffect, useState } from 'react'
import { api } from 'api'
import { config } from 'config'
import { Box, Text } from 'grommet'
import { Download as DownloadIcon } from 'grommet-icons'
import { DownloadModal } from 'components/DownloadModal'
import { Icon } from 'components/Icon'
import { Link } from 'components/Link'
import { Loader } from 'components/Loader'
import { Pill } from 'components/Pill'
import { Table } from 'components/Table'
import { formatBytes } from 'helpers/formatBytes'
import { getReadable } from 'helpers/getReadable'
import { DownloadOptionsModal } from 'components/DownloadOptionsModal'
import { useDownloadOptionsContext } from 'hooks/useDownloadOptionsContext'

export const ProjectSamplesTable = ({
  project,
  samples: defaultSamples,
  stickies = 3
}) => {
  // We only want to show the applied donwload options.
  // Also need some helpers for presentation.
  const { modality, format, getFoundFile, resourceSort } =
    useDownloadOptionsContext()
  const [loaded, setLoaded] = useState(false)
  const [samples, setSamples] = useState(defaultSamples)
  const [showDownloadOptions, setShowDownloadOptions] = useState(false)
  const hasMultiplexedData = project.has_multiplexed_data
  const infoText =
    project && project.has_bulk_rna_seq
      ? 'Bulk RNA-seq data available only when you download the entire project'
      : false

  const onOptionsSave = () => {
    setShowDownloadOptions(false)
    setLoaded(false)
  }

  // Update soring after save
  useEffect(() => {
    if (samples) {
      samples.sort(resourceSort)
      setLoaded(false)
    }
  }, [samples, modality, format])

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

  if (!loaded)
    return (
      <Box margin="64px">
        <Loader />
      </Box>
    )

  const columns = [
    {
      Header: 'Download',
      accessor: () => 'computed_files',
      Cell: ({ row }) => {
        // there is nothing available to download
        if (row.original.computed_files.length === 0) {
          return (
            <Box direction="row" align="center" gap="small">
              <DownloadIcon color="status-disabled" />
              <Box width={{ min: '120px' }}>
                <Text>Not Available</Text>
                <Text>for download</Text>
              </Box>
            </Box>
          )
        }

        const computedFile = getFoundFile(row.original.computed_files)

        if (computedFile) {
          return (
            <Box direction="row" gap="small" align="center">
              <DownloadModal
                icon={<DownloadIcon color="brand" />}
                resource={row.original}
                publicComputedFile={computedFile}
              />
              <Text>{formatBytes(computedFile.size_in_bytes)}</Text>
            </Box>
          )
        }

        // No Match for the modality/format
        return (
          <Box direction="row" align="center" gap="small">
            <DownloadIcon color="status-disabled" />
            <Box width={{ min: '120px' }}>
              <Text>Not available in</Text>
              <Text>specified format</Text>
            </Box>
          </Box>
        )
      }
    },
    {
      Header: 'Sample ID',
      accessor: ({ scpca_id: id, has_multiplexed_data: multiplexed }) => (
        <Box>
          <Text>{id}</Text>
          {multiplexed && (
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
    { Header: 'Sequencing Units', accessor: 'seq_units' },
    { Header: 'Technology', accessor: 'technologies' },
    {
      Header: 'Other Modalities',
      accessor: ({ modalities }) => (
        <>{modalities.length ? modalities.join(', ') : 'N/A'}</>
      )
    },
    { Header: 'Disease Timing', accessor: 'disease_timing' },
    { Header: 'Tissue Location', accessor: 'tissue_location' },
    {
      Header: 'Treatment',
      accessor: ({ treatment }) => treatment || 'N/A'
    },
    {
      Header: 'Age at Diagnosis',
      accessor: 'age_at_diagnosis'
    },
    { Header: 'Sex', accessor: 'sex' },
    {
      Header: 'Sample Count Estimates',
      accessor: ({ sample_cell_count_estimate: count }) => count || 'N/A'
    },
    {
      Header: () => (
        <Box direction="row" align="center">
          Est. Demux Sample Counts&nbsp;
          <Link href={config.links.what_est_demux_cell}>
            <Icon size="small" name="Help" />
          </Link>
          &nbsp;&nbsp;
        </Box>
      ),
      accessor: 'demux_cell_count_estimate',
      Cell: ({ demux_cell_count_estimate: count }) => count || 'N/A',
      isVisible: project.has_multiplexed_data
    },
    {
      Header: 'Additional Metadata Fields',
      accessor: ({ additional_metadata: data }) => Object.keys(data).join(', ')
    }
  ]

  // Add 'Multiplexed with' column only for the project with multiplexed libraries
  if (hasMultiplexedData) {
    const position = 3
    const column = {
      Header: 'Multiplexed with',
      accessor: ({ multiplexed_with: multiplexedWith }) => (
        <Box width={{ max: '200px' }} style={{ whiteSpace: ' break-spaces' }}>
          {multiplexedWith.join(', ')}
        </Box>
      )
    }

    columns.splice(position, 0, column)
  }

  return (
    <Table
      filter
      columns={columns}
      data={samples}
      stickies={stickies}
      pageSize={5}
      pageSizeOptions={[5, 10, 20, 50]}
      infoText={infoText}
    >
      <Box direction="row" gap="xlarge" pad={{ bottom: 'medium' }}>
        <Box direction="row">
          <Text weight="bold" margin={{ right: 'small' }}>
            Modality:
          </Text>
          <Text>{getReadable(modality)}</Text>
        </Box>
        <Box direction="row">
          <Text weight="bold" margin={{ right: 'small' }}>
            Data Format:
          </Text>
          <Text>{getReadable(format)}</Text>
        </Box>
        <DownloadOptionsModal
          label="Change"
          showing={showDownloadOptions}
          setShowing={setShowDownloadOptions}
          onSave={onOptionsSave}
        />
      </Box>
    </Table>
  )
}
