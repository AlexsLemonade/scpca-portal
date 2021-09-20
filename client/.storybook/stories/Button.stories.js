import React from 'react'
import { Box } from 'grommet'
import Component from 'components/Button'

const types = [
  { label: 'Default Button' },
  { primary: true, label: 'Primary Button' },
  { secondary: true, label: 'Secondary Button' }
]

export default {
  title: 'Components/Button',
  component: Component,
  args: { types }
}

export const Default = (args) => (
  <Box pad="xlarge" gap="medium">
    {args.types.map((t) => (
      <Component key={t.label} {...t} />
    ))}
  </Box>
)
