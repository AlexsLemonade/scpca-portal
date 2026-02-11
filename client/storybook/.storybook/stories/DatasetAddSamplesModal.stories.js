import React from 'react'
import { DatasetAddSamplesModal } from 'components/DatasetAddSamplesModal'
import project from 'data/project.json'

export default {
  title: 'Components/DatasetAddSamplesModal',
  args: { project }
}

export const Default = (args) => <DatasetAddSamplesModal {...args} />
