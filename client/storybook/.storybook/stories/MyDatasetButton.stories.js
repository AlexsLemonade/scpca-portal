import React from 'react'
import { Box } from 'grommet'
import { MyDatasetButton } from 'components/MyDatasetButton'

export default {
  title: 'Components/MyDatasetButton',
  args: {}
}

export const Default = (args) => {
  return (
    <Box margin="large" background="alexs-deep-blue" pad="large">
      <MyDatasetButton {...args} />
    </Box>
  )
}
