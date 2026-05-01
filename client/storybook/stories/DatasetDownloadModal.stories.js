import React from 'react'
import { DatasetDownloadModal } from '@scpca-portal/app/components/DatasetDownloadModal'

export default {
  title: 'Components/DatasetDownloadModal',
  argTypes: {
    isToken: { control: 'boolean'},
  }
}

export const Default = (args) => <DatasetDownloadModal {...args} />
