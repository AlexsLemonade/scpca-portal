import React from 'react'
import { DownloadModal } from 'components/DownloadModal'
import project from 'data/project'

export default {
  title: 'Components/DownloadModal',
  args: { resource: project }
}

export const Default = (args) => <DownloadModal {...args} />
