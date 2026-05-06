import React from 'react'
import { Box } from 'grommet'
import { Badge } from 'components/Badge'

const badges = ['Kit', 'Modality', 'SeqUnit', 'Samples']

export default {
  title: 'Components/Badge',
  component: Badge,
  args: { badges }
}

export const Default = (args) => (
  <Box pad="xlarge">
    {args.badges.map((b) => (
      <Badge key={b} badge={b} label={b} />
    ))}
  </Box>
)
