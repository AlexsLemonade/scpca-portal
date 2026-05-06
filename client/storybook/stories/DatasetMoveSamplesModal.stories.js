import React from 'react'
import { DatasetMoveSamplesModal } from '@scpca-portal/app/components/DatasetMoveSamplesModal'
import dataset from 'data/dataset.json'


export default {
  title: 'Components/DatasetMoveSamplesModal',
  args: { dataset }
}

export const Default = (args) => <DatasetMoveSamplesModal {...args} />
