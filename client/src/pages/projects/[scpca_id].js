import React, { useState } from 'react'
import { Box, Tabs, Tab, Text } from 'grommet'
import { useRouter } from 'next/router'
import { FixedContainer } from 'components/FixedContainer'
import { ProjectHeader } from 'components/ProjectHeader'
import { DetailsTable } from 'components/DetailsTable'
import { ProjectAbstractDetail } from 'components/ProjectAbstractDetail'
import { ProjectPublicationsDetail } from 'components/ProjectPublicationsDetail'
import { ProjectSamplesTable } from 'components/ProjectSamplesTable'
import { ProjectSamplesSummaryTable } from 'components/ProjectSamplesSummaryTable'
import { Link } from 'components/Link'
import { api } from 'api'
import { useResponsive } from 'hooks/useResponsive'
import { PageTitle } from 'components/PageTitle'

const Project = ({ project }) => {
  if (!project) return '404'
  const router = useRouter()
  const showSamples = router.asPath.indexOf('samples') !== -1
  const [activeIndex, setActiveIndex] = useState(showSamples ? 1 : 0)
  const onActive = (nextIndex) => setActiveIndex(nextIndex)
  const { responsive } = useResponsive()

  return (
    <FixedContainer>
      <PageTitle title={project.title} />
      <Box width="xlarge">
        <ProjectHeader project={project} />
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
                    'disease_timings',
                    'sample_count',
                    'human_readable_pi_name',
                    {
                      label: 'Contact Information',
                      value:
                        project.contacts.length > 0 ? (
                          <>
                            {project.contacts.map((contact, i) => (
                              <Text>
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
                <ProjectSamplesTable
                  project={project}
                  stickies={responsive(0, 3)}
                />
              </Box>
            </Tab>
          </Tabs>
        </Box>
      </Box>
    </FixedContainer>
  )
}

export const getServerSideProps = async ({ query }) => {
  const projectRequest = await api.projects.get(query.scpca_id)

  if (projectRequest.isOk) {
    const project = projectRequest.response
    return {
      props: { project }
    }
  }

  if (projectRequest.status === 404) {
    return { notFound: true }
  }

  return { props: { project: null } }
}

export default Project
