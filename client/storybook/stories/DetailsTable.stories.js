import React from 'react'
import { DetailsTable } from 'components/DetailsTable'
import project from 'data/project.json'

const defaultData = [
  { label: 'String', value: 'This is a string.' },
  { label: 'Array', value: ['This', 'is', 'an', 'array'] },
  { label: 'Null', value: null },
  { label: 'Undefined', value: undefined }
]

const order = ['abstract', 'disease_timings', 'human_readable_pi_name']

export default {
  title: 'Components/DetailsTable',
  args: { order, data: project, defaultData }
}

export const Default = (args) => <DetailsTable data={args.defaultData} />

export const UsingOrder = (args) => (
  <DetailsTable data={args.data} order={args.order} />
)
