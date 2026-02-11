import React from 'react'
import 'regenerator-runtime/runtime'
import { Box } from 'grommet'
import { DatasetProjectCard } from 'components/DatasetProjectCard'
import dataset from '../data/dataset.json'

const projectKeys = Object.keys(dataset.data) || []

export default {
  title: 'Components/DatasetProjectCard'
}

export const Default = () =>  (
    <>
      {projectKeys.sort().map((pId) => (
        <Box margin={{ bottom: 'large' }} key={pId}>
          <DatasetProjectCard
            dataset={dataset}
            projectId={pId}
          />
        </Box>
      ))}
    </>
)
