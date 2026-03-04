import React, { useEffect, useState } from 'react'
import { Box, Text } from 'grommet'
import { api } from 'api'
import { ProjectSamplesTableContextProvider } from 'contexts/ProjectSamplesTableContext'
import { useRouter } from 'next/router'
import { useScrollRestore } from 'hooks/useScrollRestore'
import { useMyDataset } from 'hooks/useMyDataset'
import { ProjectSamplesTable } from 'components/ProjectSamplesTable'
import { ProjectSamplesTableOptionsHeader } from 'components/ProjectSamplesTableOptionsHeader'
import { DatasetSaveAndGoBackButton } from 'components/DatasetSaveAndGoBackButton'
import { Button } from 'components/Button'
import { Link } from 'components/Link'
import { Loader } from 'components/Loader'

export const ViewEditSamples = ({ project }) => {
  const { asPath, back } = useRouter()
  const { setRestoreFromDestination } = useScrollRestore()
  const {
    myDataset,
    getMyDatasetProjectSamples,
    isMyDatasetProjectIncludeBulk,
    isMyDatasetProjectMerged
  } = useMyDataset()

  const [loading, setLoading] = useState(true)
  const [samples, setSamples] = useState([])
  // For dataset download options
  const [includeBulk, setIncludeBulk] = useState(false)
  const [includeMerge, setIncludeMerge] = useState(false)

  //  Set up the dataset table and options after component mounts
  useEffect(() => {
    // Check to see if myDataset exists or if project was removed from myDataset
    if (!myDataset?.data[project.scpca_id]) return
    // Filter to display only samples from My Dataset
    setSamples(getMyDatasetProjectSamples(project))
    // Preselect download options based on the values in myDataset
    setIncludeBulk(isMyDatasetProjectIncludeBulk(project))
    setIncludeMerge(isMyDatasetProjectMerged(project))
    setLoading(false)
  }, [myDataset])

  const handleBackToMyDataset = () => {
    setRestoreFromDestination(asPath)
    back()
  }

  if (loading) return <Loader />

  return (
    <Box gap="large" fill margin={{ bottom: 'large' }}>
      <Box align="start" gap="large">
        <Button label="Back to My Dataset" onClick={handleBackToMyDataset} />
        <Link href={`/projects/${project.scpca_id}`} newTab>
          <Text weight="bold" color="brand" size="large">
            {project.title}
          </Text>
        </Link>
      </Box>
      <ProjectSamplesTableContextProvider
        project={project}
        samples={samples}
        canRemove
      >
        <Box pad={{ bottom: 'medium' }}>
          <ProjectSamplesTableOptionsHeader
            project={project}
            includeBulk={includeBulk}
            includeMerge={includeMerge}
            onIncludeBulkChange={setIncludeBulk}
            onIncludeMergeChange={setIncludeMerge}
          />
        </Box>
        <ProjectSamplesTable>
          <Box direction="row" justify="end" margin={{ vertical: 'medium' }}>
            <DatasetSaveAndGoBackButton
              project={project}
              includeBulk={includeBulk}
              includeMerge={includeMerge}
            />
          </Box>
        </ProjectSamplesTable>
      </ProjectSamplesTableContextProvider>
    </Box>
  )
}

export const getServerSideProps = async ({ query }) => {
  const projectId = query.project_id
  const projectRequest = await api.projects.get(projectId)

  if (projectRequest.isOk) {
    return {
      props: {
        project: projectRequest.response
      }
    }
  }

  return { notFound: true }
}

export default ViewEditSamples
