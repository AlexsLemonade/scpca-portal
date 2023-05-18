import React from 'react'
import { ProjectHeader } from 'components/ProjectHeader'
import project from 'data/project'

export default {
  title: 'Components/ProjectHeader',
  args: { project }
}

export const Default = (args) => <ProjectHeader {...args} />
