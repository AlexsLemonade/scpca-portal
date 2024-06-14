import React, { useEffect, useState } from 'react'
import { api } from 'api'
import { config } from 'config'
import { Box, Text } from 'grommet'
import { Download as DownloadIcon } from 'grommet-icons'
import { useDownloadOptionsContext } from 'hooks/useDownloadOptionsContext'
import { useMetadataOnly } from 'hooks/useMetadataOnly'
import { formatBytes } from 'helpers/formatBytes'
import { getReadable } from 'helpers/getReadable'
import { DownloadModal } from 'components/DownloadModal'
import { DownloadOptionsModal } from 'components/DownloadOptionsModal'
import { Icon } from 'components/Icon'
import { Link } from 'components/Link'
import { Loader } from 'components/Loader'
import { Pill } from 'components/Pill'
import { Table } from 'components/Table'

import { WarningAnnDataMultiplexed } from 'components/WarningAnnDataMultiplexed'

export const ProjectSamplesTable = ({
  project,
  samples: defaultSamples,
  stickies = 3
}) => {
  // We only want to show the applied donwload options.
  // Also need some helpers for presentation.
  const { modality, format, getFoundFile } = useDownloadOptionsContext()
  const { metadataComputedFile } = useMetadataOnly(project.computed_files)
  const [loaded, setLoaded] = useState(false)
  const [samples, setSamples] = useState(defaultSamples)
  const [showDownloadOptions, setShowDownloadOptions] = useState(false)
  const [currentFilter, setCurrentFilter] = useState('') // For storing globalFiter for metadata only download
  const hasMultiplexedData = project.has_multiplexed_data
  const infoText =
    project && project.has_bulk_rna_seq
      ? 'Bulk RNA-seq data available only when you download the entire project'
      : false

  const onFilterChange = (value) => {
    setCurrentFilter(value)
  }

  const onOptionsSave = () => {
    setShowDownloadOptions(false)
    setLoaded(false)
  }

  // Update after save
  useEffect(() => {
    if (samples) setLoaded(false)
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
      id: 'download',
      accessor: ({ computed_files: computedFiles }) => {
        if (computedFiles.length === 0) return -1
        const computedFile = getFoundFile(computedFiles)
        return computedFile ? computedFile.size_in_bytes : 0
      },
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

        const computedFile = getFoundFile(row.original.computed_files, true)

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
      id: 'demux_cell_count_estimate',
      Header: () => (
        <Box direction="row" align="center">
          Est. Demux Sample Counts&nbsp;
          <Link href={config.links.what_est_demux_cell}>
            <Icon size="small" name="Help" />
          </Link>
          &nbsp;&nbsp;
        </Box>
      ),
      accessor: ({ demux_cell_count_estimate: count }) => count || 'N/A',
      isVisible: hasMultiplexedData
    },
    {
      Header: 'Additional Metadata Fields',
      accessor: ({ additional_metadata: data }) => Object.keys(data).join(', ')
    }
  ]

  return (
    <Table
      filter
      columns={columns}
      data={samples}
      stickies={stickies}
      pageSize={5}
      pageSizeOptions={[5, 10, 20, 50]}
      infoText={infoText}
      defaultSort={[{ id: 'download', desc: true }]}
      onFilterChange={onFilterChange}
    >
      <Box direction="row" justify="between" pad={{ bottom: 'medium' }}>
        <Box direction="row" gap="xlarge" align="center">
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
        <Box>
          <DownloadModal
            disabled={currentFilter}
            label="Download Sample Metadata"
            icon={<DownloadIcon color="brand" />}
            resource={project}
            publicComputedFile={metadataComputedFile}
          />
        </Box>
      </Box>
      {project.has_multiplexed_data && format === 'ANN_DATA' && (
        <WarningAnnDataMultiplexed />
      )}
    </Table>
  )
}
