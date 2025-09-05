import React, { useEffect, useState } from 'react'
import { Box, Text } from 'grommet'
import { api } from 'api'
import { DatasetSamplesTableContextProvider } from 'contexts/DatasetSamplesTableContext'
import { useRouter } from 'next/router'
import { useScrollPosition } from 'hooks/useScrollPosition'
import { useDatasetManager } from 'hooks/useDatasetManager'
import { DatasetSamplesTable } from 'components/DatasetSamplesTable'
import { DatasetSamplesTableOptionsHeader } from 'components/DatasetSamplesTableOptionsHeader'
import { Button } from 'components/Button'
import { Link } from 'components/Link'
import { Loader } from 'components/Loader'

export const ViewEditSamples = ({ project }) => {
  const { back } = useRouter()
  const { setRestoreScrollPosition } = useScrollPosition()
  const {
    myDataset,
    getAddedProjectDataSamples,
    isProjectIncludeBulk,
    isProjectMerged
  } = useDatasetManager()

  const [loading, setLoading] = useState(true)
  const [samplesInMyDataset, setSamplesInMyDataset] = useState([])
  // For dataset download options
  const [includeBulk, setIncludeBulk] = useState(false)
  const [includeMerge, setIncludeMerge] = useState(false)

  // Configure the dataset table and options after component mounts
  useEffect(() => {
    if (!myDataset) return
    // Filter to display only samples from My Dataset
    setSamplesInMyDataset(getAddedProjectDataSamples(project))
    // Preselect download options based on the values in myDataset
    setIncludeBulk(isProjectIncludeBulk(project))
    setIncludeMerge(isProjectMerged(project))
    setLoading(false)
  }, [myDataset])

  const handleBackToMyDataset = () => {
    const source = '/download' // The page to navigating back to
    setRestoreScrollPosition(source)
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
      <DatasetSamplesTableContextProvider>
        <Box pad={{ bottom: 'medium' }}>
          <DatasetSamplesTableOptionsHeader
            project={project}
            includeBulk={includeBulk}
            includeMerge={includeMerge}
            onIncludeBulkChange={setIncludeBulk}
            onIncludeMergeChange={setIncludeMerge}
          />
        </Box>
        <DatasetSamplesTable
          project={project}
          samples={samplesInMyDataset}
          editable
        />
      </DatasetSamplesTableContextProvider>
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
