import React from 'react'
import { Box } from 'grommet'
import { Badge as Component } from 'components/Badge'

const badges = ['Kit', 'Modality', 'SeqUnit', 'Samples']

export default {
  title: 'Components/Badge',
  component: Component,
  args: { badges }
}

export const Default = (args) => (
  <Box pad="xlarge">
    {args.badges.map((b) => (
      <Component key={b} badge={b} label={b} />
    ))}
  </Box>
)
