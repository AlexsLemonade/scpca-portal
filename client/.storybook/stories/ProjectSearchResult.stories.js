import React from 'react'
import { ProjectSearchResult as Component } from 'components/ProjectSearchResult'
import project from '../data/project'

export default {
  title: 'Components/ProjectSearchResult',
  component: Component,
  args: { project }
}

export const Default = (args) => <Component project={args.project} />
