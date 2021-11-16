import React from 'react'
import { ProjectSamplesTable } from 'components/ProjectSamplesTable'
import samples from '../data/samples'

export default {
  title: 'Components/ProjectSamplesTable',
  args: { samples }
}

export const Default = (args) => <ProjectSamplesTable samples={args.samples} />

export const OnePage = (args) => (
  <ProjectSamplesTable samples={args.samples.slice(0, 10)} />
)
