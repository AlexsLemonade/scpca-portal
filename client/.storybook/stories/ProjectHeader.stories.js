import React from 'react'
import { ProjectHeader as Component } from 'components/ProjectHeader'
import project from '../data/project'

export default {
  title: 'Components/ProjectHeader',
  component: Component,
  args: { project }
}

export const Default = (args) => <Component project={args.project} />
