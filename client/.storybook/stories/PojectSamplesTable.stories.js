import React from 'react'
import { ProjectSamplesTable as Component } from 'components/ProjectSamplesTable'
import samples from '../data/samples'

export default {
  title: 'Components/ProjectSamplesTable',
  component: Component,
  args: { samples }
}

export const Default = (args) => <Component samples={args.samples} />
