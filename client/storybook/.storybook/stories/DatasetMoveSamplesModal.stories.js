import React from 'react'
import { DatasetMoveSamplesModal } from 'components/DatasetMoveSamplesModal'
import dataset from 'data/user_dataset.json'


export default {
  title: 'Components/DatasetMoveSamplesModal',
  args: { dataset }
}

export const Default = (args) => <DatasetMoveSamplesModal {...args} />
