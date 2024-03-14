import React from 'react'
import 'regenerator-runtime/runtime'
import { DownloadOptionsContextProvider } from 'contexts/DownloadOptionsContext'
import { ProjectSamplesTable } from 'components/ProjectSamplesTable'
import project from 'data/project'

export default {
  title: 'Components/ProjectSamplesTable',
  args: { project, samples: project.samples }
}

export const Default = (args) => (
  <DownloadOptionsContextProvider attribute="samples" resource={project}>
    <ProjectSamplesTable {...args} />
  </DownloadOptionsContextProvider>
)

export const OnePage = (args) => (
  <DownloadOptionsContextProvider attribute="samples" resource={project}>
    <ProjectSamplesTable project={project} samples={args.samples.slice(0, 5)} />
  </DownloadOptionsContextProvider>
)
