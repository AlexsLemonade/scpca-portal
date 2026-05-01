import React from 'react'
import { ProjectSamplesSummaryTable } from '@scpca-portal/app/components/ProjectSamplesSummaryTable'
import project from '@scpca-portal/storybook/data/project.json'

export default {
  title: 'Components/ProjectSamplesSummaryTable',
  args: { summaries: project.summaries }
}

export const Default = (args) => <ProjectSamplesSummaryTable {...args} />
