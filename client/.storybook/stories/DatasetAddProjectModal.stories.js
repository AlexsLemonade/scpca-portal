import React from 'react'
import 'regenerator-runtime/runtime'
import { Box, Heading } from 'grommet'
import { DatasetAddProjectModal } from 'components/DatasetAddProjectModal'
import projects from 'data/projects'

const projectIds = {
    SCPCP000001: 'Single-cell with Bulk RNA-seq',
    SCPCP000004: 'Single-cell',
    SCPCP000006: 'Spatial',
    SCPCP000009: 'Single-cell with multiplexed samples',
}

export default {
  title: 'Components/DatasetAddProjectModal'
}

export const Default = (args) =>  (
    <>
     {projects.map((project)=> (
        <>
            <Heading level={4} margin={{ top: 'medium', bottom: '0' }}>
                {project.scpca_id}
            </Heading>
            <Box margin={{ bottom: 'small' }}>
                ({projectIds[project.scpca_id]})
            </Box>
            <Box width='160px'>
                <DatasetAddProjectModal project={project} />
            </Box>
        </>
     ))}
    </>
)
