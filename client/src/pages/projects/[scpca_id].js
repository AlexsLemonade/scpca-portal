import React, { useEffect, useState } from 'react'
import { Box, Tabs, Tab, Text } from 'grommet'
import { useRouter } from 'next/router'
import { useMyDataset } from 'hooks/useMyDataset'
import { useResponsive } from 'hooks/useResponsive'
import { CCDLDatasetDownloadModalContextProvider } from 'contexts/CCDLDatasetDownloadModalContext'
import { ProjectSamplesTableContextProvider } from 'contexts/ProjectSamplesTableContext'
import { api } from 'api'
import { allModalities } from 'config/datasets'
import { differenceArray } from 'helpers/differenceArray'
import { DatasetAddSamplesModal } from 'components/DatasetAddSamplesModal'
import { DetailsTable } from 'components/DetailsTable'
import { Link } from 'components/Link'
import { PageTitle } from 'components/PageTitle'
import { ProjectHeader } from 'components/ProjectHeader'
import { ProjectAbstractDetail } from 'components/ProjectAbstractDetail'
import { ProjectAdditionalRestrictions } from 'components/ProjectAdditionalRestrictions'
import { ProjectPublicationsDetail } from 'components/ProjectPublicationsDetail'
import { ProjectExternalAccessionsDetail } from 'components/ProjectExternalAccessionsDetail'
import { ProjectSamplesTable } from 'components/ProjectSamplesTable'
import { ProjectSamplesSummaryTable } from 'components/ProjectSamplesSummaryTable'

const Project = ({ project, ccdlDatasets }) => {
  const { myDataset, getMyDatasetProjectDataSamples } = useMyDataset()
  const { responsive } = useResponsive()

  const router = useRouter()

  const showSamples = router.asPath.indexOf('samples') !== -1

  const [activeIndex, setActiveIndex] = useState(showSamples ? 1 : 0)
  const onActive = (nextIndex) => setActiveIndex(nextIndex)

  const [disableAddToDatasetModal, setDisableAddToDatasetModal] =
    useState(false)

  const ccdlDataDatasets = ccdlDatasets.filter((d) => d.format !== 'METADATA')
  const ccdlMetadataDatasets = ccdlDatasets.filter(
    (d) => d.format === 'METADATA'
  )

  // Disable DatasetAddSamplesModal if all samples are added
  useEffect(() => {
    const datasetProjectData = getMyDatasetProjectDataSamples(project)
    const samplesLeft = allModalities
      .map((m) =>
        differenceArray(project.modality_samples[m], datasetProjectData[m])
      )
      .flat()

    setDisableAddToDatasetModal(samplesLeft.length === 0)
  }, [myDataset])

  if (!project) return '404'

  return (
    <>
      <PageTitle title={project.title} />
      <Box width="xlarge">
        <CCDLDatasetDownloadModalContextProvider
          project={project}
          datasets={ccdlDataDatasets}
        >
          <ProjectHeader project={project} />
        </CCDLDatasetDownloadModalContextProvider>
        <Box pad={{ vertical: 'large' }}>
          <Tabs activeIndex={activeIndex} onActive={onActive}>
            <Tab title="Project Details">
              <Box pad={{ vertical: 'large' }}>
                <DetailsTable
                  data={project}
                  order={[
                    {
                      label: 'Abstract',
                      value: (
                        <ProjectAbstractDetail abstract={project.abstract} />
                      )
                    },
                    {
                      label: 'Publications',
                      value:
                        project.publications.length > 0 ? (
                          <ProjectPublicationsDetail
                            publications={project.publications}
                          />
                        ) : (
                          ''
                        )
                    },
                    {
                      label: 'Also deposited under',
                      value:
                        project.external_accessions.length > 0 ? (
                          <ProjectExternalAccessionsDetail
                            externalAccessions={project.external_accessions}
                          />
                        ) : (
                          ''
                        )
                    },
                    {
                      label: 'DOI',
                      value:
                        project.publications.length > 0 ? (
                          <Text>
                            {project.publications.map((publication) => (
                              <Box key={publication.doi}>
                                <Link
                                  label={publication.doi}
                                  href={publication.doi_url}
                                />
                              </Box>
                            ))}
                          </Text>
                        ) : (
                          ''
                        )
                    },
                    {
                      label: 'disease_timings',
                      value:
                        project.disease_timings.length > 0 ? (
                          <Text>{project.disease_timings.join(', ')}</Text>
                        ) : (
                          ''
                        )
                    },

                    'sample_count',
                    'human_readable_pi_name',
                    {
                      label: 'Contact Information',
                      value:
                        project.contacts.length > 0 ? (
                          <>
                            {project.contacts.map((contact, i) => (
                              <Text key={contact}>
                                {i ? ', ' : ''}
                                <Link
                                  key={contact.name}
                                  label={`${contact.name} <${contact.email}>`}
                                  href={`mailto:${contact.email}`}
                                />
                              </Text>
                            ))}
                          </>
                        ) : (
                          ''
                        )
                    },
                    {
                      label: 'Additional Restrictions',
                      value: (
                        <ProjectAdditionalRestrictions
                          text={project.additional_restrictions || 'Pending'}
                        />
                      )
                    }
                  ]}
                />
              </Box>
              <Text size="large" weight="bold">
                Sample Summary
              </Text>
              <Box
                pad={{ vertical: 'medium' }}
                width={{ max: 'full' }}
                overflow="auto"
              >
                <ProjectSamplesSummaryTable summaries={project.summaries} />
              </Box>
            </Tab>
            <Tab title="Sample Details">
              <Box
                pad={{ vertical: 'medium' }}
                width={{ max: 'full' }}
                overflow="auto"
              >
                <CCDLDatasetDownloadModalContextProvider
                  project={project}
                  datasets={ccdlMetadataDatasets}
                >
                  <ProjectSamplesTableContextProvider
                    project={project}
                    samples={project.samples}
                    canAdd
                  >
                    <Box direction="row" justify="end">
                      <DatasetAddSamplesModal
                        project={project}
                        samples={project.samples}
                        disabled={disableAddToDatasetModal}
                      />
                    </Box>
                    <ProjectSamplesTable stickies={responsive(0, 3)}>
                      <Box
                        direction="row"
                        justify="end"
                        margin={{ vertical: 'medium' }}
                      >
                        <DatasetAddSamplesModal
                          project={project}
                          samples={project.samples}
                          disabled={disableAddToDatasetModal}
                        />
                      </Box>
                    </ProjectSamplesTable>
                  </ProjectSamplesTableContextProvider>
                </CCDLDatasetDownloadModalContextProvider>
              </Box>
            </Tab>
          </Tabs>
        </Box>
      </Box>
    </>
  )
}

export const getServerSideProps = async ({ query: projectQuery }) => {
  const ccdlDatasetQuery = {
    ccdl_project_id: projectQuery.scpca_id,
    limit: 100
  }

  const [projectRequest, ccdlDatasetRequest] = await Promise.all([
    api.projects.get(projectQuery.scpca_id),
    api.ccdlDatasets.list(ccdlDatasetQuery)
  ])

  if (projectRequest.isOk && ccdlDatasetRequest.isOk) {
    const project = projectRequest.response
    const { results: ccdlDatasets } = ccdlDatasetRequest.response
    return {
      props: { project, ccdlDatasets }
    }
  }

  if (projectRequest.status === 404) {
    return { notFound: true }
  }

  return { props: { project: null, ccdlDatasets: null } }
}

export default Project
