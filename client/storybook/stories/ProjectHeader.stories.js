import React from 'react'
import { ProjectHeader } from '@scpca-portal/app/components/ProjectHeader'
import project from '@scpca-portal/storybook/data/project.json'

export default {
  title: 'Components/ProjectHeader',
  args: { project }
}

export const Default = (args) => <ProjectHeader {...args} />
