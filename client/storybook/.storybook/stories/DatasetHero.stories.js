import React from 'react'
import { DatasetHero } from 'components/DatasetHero'

  const datasets = [{
      id: 1,
      is_processing: true,
      is_processed: false,
      is_errored: false,
      is_expired: false
    },
    { id: 3,
        is_processing: false,
        is_processed: true,
        is_errored: false,
        is_expired: true
      },
      {
        id: 2,
        is_processing: false,
        is_processed: true,
        is_errored: false,
        is_expired: false
      }
     ]

const isToken = false // For Storybook Control for toggling DownloadReady token (with or without)

export default {
  title: 'Components/DatasetHero',
  args: {datasets, isToken},
  argTypes: {
    isToken: { control: 'boolean'}
  }
}

export const Default = (args) =>
<>{
    datasets.map((d) => <DatasetHero key={d.id} dataset={d} {...args} />)}</>
