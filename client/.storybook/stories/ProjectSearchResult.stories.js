import React from 'react'
import { ProjectSearchResult } from 'components/ProjectSearchResult'
import project from 'data/project'

export default {
  title: 'Components/ProjectSearchResult',
  args: { project }
}

export const Default = (args) => <ProjectSearchResult {...args} />
