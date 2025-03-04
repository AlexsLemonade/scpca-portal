import React from 'react'
import 'regenerator-runtime/runtime'
import { Box, Heading } from 'grommet'
import { DatasetOptionsContextProvider } from 'contexts/DatasetOptionsContext'
import { DatasetAddToModal } from 'components/DatasetAddToModal'
import projects from 'data/projects'

export default {
  title: 'Components/DatasetAddToModal'
}

export const Default = (args) => (
    <Box pad="xlarge" width='medium'>
     {projects.map((project)=> (
        <DatasetOptionsContextProvider key={project.scpca_id} resource={project}>
            <Heading level={4} margin={{ top: 'medium', bottom: '0' }}>{project.scpca_id}</Heading>
            <Box margin={{ bottom: 'small' }}>({project.heading})</Box>
            <Box width='160px'>
                <DatasetAddToModal resource={project}/>
            </Box>
        </DatasetOptionsContextProvider>
     ))}
    </Box>
)
