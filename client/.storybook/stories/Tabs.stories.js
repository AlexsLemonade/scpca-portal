import React from 'react'
import { Box, Tabs, Tab } from 'grommet'

export default {
  title: 'Components/Tabs',
  component: Tabs
}

export const Default = () => (
  <Tabs>
    <Tab title="Project Details">
      <Box pad="medium">One</Box>
    </Tab>
    <Tab title="Sample Details">
      <Box pad="medium">Two</Box>
    </Tab>
  </Tabs>
)
