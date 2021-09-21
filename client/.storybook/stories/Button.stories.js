import React from 'react'
import { Box } from 'grommet'
import { Button } from 'components/Button'

const types = [
  { label: 'Default Button' },
  { primary: true, label: 'Primary Button' },
  { secondary: true, label: 'Secondary Button' }
]

export default {
  title: 'Components/Button',
  component: Button,
  args: { types }
}

export const Default = (args) => (
  <Box pad="xlarge" gap="medium" direction="row">
    {args.types.map((t) => (
      <Button key={t.label} {...t} />
    ))}
  </Box>
)
