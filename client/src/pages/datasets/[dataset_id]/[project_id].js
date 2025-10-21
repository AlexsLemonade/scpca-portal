import React, { useEffect, useState } from 'react'
import { Box, Text } from 'grommet'
import { api } from 'api'
import { ProjectSamplesTableContextProvider } from 'contexts/ProjectSamplesTableContext'
import { useRouter } from 'next/router'
import { useScrollRestore } from 'hooks/useScrollRestore'
import { useDataset } from 'hooks/useDataset'
import { ProjectSamplesTable } from 'components/ProjectSamplesTable'
import { ProjectSamplesTableOptionsHeader } from 'components/ProjectSamplesTableOptionsHeader'
import { Button } from 'components/Button'
import { Link } from 'components/Link'
import { Loader } from 'components/Loader'

export const ViewSamples = ({ dataset, project }) => {
  const { asPath, back } = useRouter()
  const { setRestoreFromDestination } = useScrollRestore()
  const { isProjectIncludeBulk, isProjectMerged, getDatasetProjectSamples } =
    useDataset()

  const [loading, setLoading] = useState(true)
  const [samples, setSamples] = useState([])

  // For dataset download options
  const [includeBulk, setIncludeBulk] = useState(false)
  const [includeMerge, setIncludeMerge] = useState(false)

  // Set up the dataset table on component mount
  useEffect(() => {
    // Filter to display only samples from dataset
    setSamples(getDatasetProjectSamples(dataset, project))
    // Preselect download options based on the values in dataset
    setIncludeBulk(isProjectIncludeBulk(dataset, project))
    setIncludeMerge(isProjectMerged(dataset, project))
    setLoading(false)
  }, [])

  const handleBackToDataset = () => {
    setLoading(true)
    setRestoreFromDestination(asPath)
    back()
  }

  if (loading) return <Loader />

  return (
    <Box gap="large" fill margin={{ bottom: 'large' }}>
      <Box align="start" gap="large">
        <Button label="Back to Dataset" onClick={handleBackToDataset} />
        <Link href={`/projects/${project.scpca_id}`} newTab>
          <Text weight="bold" color="brand" size="large">
            {project.title}
          </Text>
        </Link>
      </Box>
      <ProjectSamplesTableContextProvider>
        <Box pad={{ bottom: 'medium' }}>
          <ProjectSamplesTableOptionsHeader
            project={project}
            includeBulk={includeBulk}
            includeMerge={includeMerge}
            onIncludeBulkChange={setIncludeBulk}
            onIncludeMergeChange={setIncludeMerge}
            readOnly
          />
        </Box>
        <ProjectSamplesTable
          project={project}
          samples={samples}
          dataset
          readOnly
        />
      </ProjectSamplesTableContextProvider>
    </Box>
  )
}

export const getServerSideProps = async ({ query }) => {
  const [datasetRequest, projectRequest] = await Promise.all([
    api.datasets.get(query.dataset_id),
    api.projects.get(query.project_id)
  ])

  if (projectRequest.isOk && datasetRequest.isOk) {
    return {
      props: {
        dataset: datasetRequest.response,
        project: projectRequest.response
      }
    }
  }

  return { notFound: true }
}

export default ViewSamples
