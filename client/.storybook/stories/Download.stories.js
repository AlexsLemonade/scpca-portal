import React from 'react'
import { Download } from 'components/Download'
import project from 'data/project'

export default {
  title: 'Components/Download',
  args: { resource: project }
}

export const Default = (args) => <Download {...args} />
