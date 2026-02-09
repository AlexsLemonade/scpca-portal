import React from 'react'
import { ProjectSamplesSummaryTable } from 'components/ProjectSamplesSummaryTable'
import project from 'data/project'

export default {
  title: 'Components/ProjectSamplesSummaryTable',
  args: { summaries: project.summaries }
}

export const Default = (args) => <ProjectSamplesSummaryTable {...args} />
