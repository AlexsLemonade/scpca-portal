import React from 'react'
import { DatasetHero } from 'components/DatasetHero'

const datasets = [
  {
    id: 1,
    state: 'PROCESSING',
    is_expired: true
  },
  { id: 3, state: 'SUCCEEDED', is_expired: true },
  {
    id: 2,
    state: 'SUCCEEDED',
    is_expired: false
  }
]

const isToken = false // For Storybook Control for toggling DownloadReady token (with or without)

export default {
  title: 'Components/DatasetHero',
  args: { datasets, isToken },
  argTypes: {
    isToken: { control: 'boolean' }
  }
}

export const Default = (args) => (
  <>
    {datasets.map((d) => (
      <DatasetHero key={d.id} dataset={d} {...args} />
    ))}
  </>
)
