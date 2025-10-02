import React, { useEffect, useState } from 'react'
import { Box, Text } from 'grommet'
import { api } from 'api'
import { DatasetSamplesTableContextProvider } from 'contexts/DatasetSamplesTableContext'
import { useRouter } from 'next/router'
import { useScrollRestore } from 'hooks/useScrollRestore'
import { useMyDataset } from 'hooks/useMyDataset'
import { DatasetSamplesTable } from 'components/DatasetSamplesTable'
import { DatasetSamplesTableOptionsHeader } from 'components/DatasetSamplesTableOptionsHeader'
import { Button } from 'components/Button'
import { Link } from 'components/Link'
import { Loader } from 'components/Loader'

export const ViewEditSamples = ({ project }) => {
  const { asPath, back } = useRouter()
  const { setRestoreFromDestination } = useScrollRestore()
  const {
    myDataset,
    getAddedProjectDataSamples,
    isProjectIncludeBulk,
    isProjectMerged
  } = useMyDataset()

  const [loading, setLoading] = useState(true)
  const [samples, setSamples] = useState([])
  // For dataset download options
  const [includeBulk, setIncludeBulk] = useState(false)
  const [includeMerge, setIncludeMerge] = useState(false)

  //  Set up the dataset table and options after component mounts
  useEffect(() => {
    if (!myDataset) return
    // Filter to display only samples from My Dataset
    setSamples(getAddedProjectDataSamples(project))
    // Preselect download options based on the values in myDataset
    setIncludeBulk(isProjectIncludeBulk(project))
    setIncludeMerge(isProjectMerged(project))
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
        <DatasetSamplesTable project={project} samples={samples} editable />
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
