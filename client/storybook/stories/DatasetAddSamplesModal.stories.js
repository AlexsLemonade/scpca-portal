import React from 'react'
import { DatasetAddSamplesModal } from '@scpca-portal/app/components/DatasetAddSamplesModal'
import project from '@scpca-portal/storybook/data/project.json'

export default {
  title: 'Components/DatasetAddSamplesModal',
  args: { project }
}

export const Default = (args) => <DatasetAddSamplesModal {...args} />
