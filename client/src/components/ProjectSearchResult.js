import React from 'react'
import { Box, Text } from 'grommet'
import { Download as DownloadIcon } from 'grommet-icons'
import { useResponsive } from 'hooks/useResponsive'
import { Button } from 'components/Button'
import { Link } from 'components/Link'
import { CCDLDatasetDownloadModal } from 'components/CCDLDatasetDownloadModal'
import { ProjectHeader } from 'components/ProjectHeader'
import { ProjectAbstractDetail } from 'components/ProjectAbstractDetail'
import { ProjectPublicationsDetail } from 'components/ProjectPublicationsDetail'
import { ProjectExternalAccessionsDetail } from 'components/ProjectExternalAccessionsDetail'
import { formatDiagnosisCounts } from 'helpers/formatCounts'
import { CCDLDatasetDownloadContextProvider } from 'contexts/CCDLDatasetDownloadContext'

export const ProjectSearchResult = ({ project }) => {
  const { responsive } = useResponsive()

  const searchDetails = [
    {
      title: 'Diagnosis',
      value:
        Object.keys(project.diagnoses_counts).length > 0 ? (
          <Text>
            {formatDiagnosisCounts(project.diagnoses_counts).join(', ')}
          </Text>
        ) : (
          ''
        )
    },
    {
      title: 'Abstract',
      value: <ProjectAbstractDetail abstract={project.abstract} />
    },
    {
      title: 'Publications',
      value:
        project.publications.length > 0 ? (
          <ProjectPublicationsDetail publications={project.publications} />
        ) : (
          ''
        )
    },
    {
      title: 'Also deposited under',
      value:
        project.external_accessions.length > 0 ? (
          <ProjectExternalAccessionsDetail
            inline
            externalAccessions={project.external_accessions}
          />
        ) : (
          ''
        )
    },
    {
      title: 'Additional Sample Metadata Fields',
      value:
        project.publications.length > 0 ? (
          <Text>{project.additional_metadata_keys.join(', ')}</Text>
        ) : (
          ''
        )
    }
  ]
  return (
    <Box elevation="medium" pad="medium" width="full">
      <ProjectHeader linked project={project} />
      <Box border={{ side: 'top' }} margin={{ top: 'medium' }}>
        {searchDetails.map((d) => (
          <Box key={d.title} pad={{ top: 'medium' }}>
            <Text weight="bold">{d.title}</Text>
            {d.value ? (
              <Text>{d.value}</Text>
            ) : (
              <Text italic color="black-tint-30">
                Not Specified
              </Text>
            )}
          </Box>
        ))}
      </Box>
      <Box
        align={responsive('start', 'center')}
        direction={responsive('column', 'row')}
        gap="small"
        pad={{ top: 'medium' }}
      >
        <Link href={`/projects/${project.scpca_id}#samples`}>
          <Button label="View Samples" aria-label="View Samples" />
        </Link>
        <CCDLDatasetDownloadContextProvider
          project={project}
          datasets={project.datasets.filter((d) => d.format === 'METADATA')}
        >
          <CCDLDatasetDownloadModal
            label="Download Sample Metadata"
            icon={<DownloadIcon color="brand" />}
          />
        </CCDLDatasetDownloadContextProvider>
      </Box>
    </Box>
  )
}

export default ProjectSearchResult
