import React from 'react'
import { Box } from 'grommet'

export const ViewEditSamples = ({ projectId }) => {
  return <Box>ViewEditSamples: {projectId}</Box>
}

export const getServerSideProps = async ({ query }) => ({
  props: { projectId: query.project_id }
})

export default ViewEditSamples
