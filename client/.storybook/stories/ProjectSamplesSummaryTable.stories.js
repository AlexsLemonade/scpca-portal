import React from 'react'
import { ProjectSamplesSummaryTable } from 'components/ProjectSamplesSummaryTable'
import project from '../data/project'

export default {
  title: 'Components/ProjectSamplesSummaryTable',
  args: { project }
}

export const Default = (args) => (
  <ProjectSamplesSummaryTable summaries={args.project.summaries} />
)
