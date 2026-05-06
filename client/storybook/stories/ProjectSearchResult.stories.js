import React from 'react'
import { ProjectSearchResult } from '@scpca-portal/app/components/ProjectSearchResult'
import project from 'data/project.json'
import dataset from 'data/dataset.json'

export default {
  title: 'Components/ProjectSearchResult',
  args: { project, ccdlDatasets: [dataset] }
}

export const Default = (args) => <ProjectSearchResult {...args} />
