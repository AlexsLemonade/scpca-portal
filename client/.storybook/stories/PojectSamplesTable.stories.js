import React from 'react'
import { ProjectSamplesTable } from 'components/ProjectSamplesTable'
import project from 'data/project'

export default {
  title: 'Components/ProjectSamplesTable',
  args: { project, samples: project.samples }
}

export const Default = (args) => <ProjectSamplesTable {...args} />

export const OnePage = (args) => (
  <ProjectSamplesTable project={project} samples={args.samples.slice(0, 5)} />
)
