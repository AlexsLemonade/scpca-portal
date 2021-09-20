import React from 'react'
import { Box } from 'grommet'
import Component from 'components/DetailsTable'

const data = [
  { label: 'Abstract', value: 'The Abstract here' },
  { label: 'Disease Timing', value: 60 },
  { label: 'Primary Investigator', value: 'Dr. Jorklyn' }
]

const order = ['abstract', 'disease_timings', 'pi_name']

export default {
  title: 'Components/DetailsTable',
  component: Component,
  args: { order, data }
}

export const Default = (args) => (
  <Component data={args.data} order={args.order} />
)

export const UsingOrder = (args) => (
  <Component data={args.data} order={args.order} />
)
