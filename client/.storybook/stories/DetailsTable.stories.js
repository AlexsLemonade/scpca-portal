import React from 'react'
import { Box } from 'grommet'
import { DetailsTable } from 'components/DetailsTable'
import project from '../data/project'

const order = ['abstract', 'disease_timings', 'human_readable_pi_name']

export default {
  title: 'Components/DetailsTable',
  args: { order, data: project }
}

export const Default = (args) => (
  <DetailsTable data={args.data} order={args.order} />
)

export const UsingOrder = (args) => (
  <DetailsTable data={args.data} order={args.order} />
)
