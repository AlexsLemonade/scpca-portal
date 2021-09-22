import React from 'react'
import { Box, Paragraph } from 'grommet'
import Kit from '../images/badges/kit.svg'
import Modality from '../images/badges/modality.svg'
import SeqUnit from '../images/badges/seq-unit.svg'
import Samples from '../images/badges/samples.svg'

const badges = {
  Kit,
  Modality,
  SeqUnit,
  Samples
}

export const Badge = ({ badge, label }) => {
  const BadgeSVG = badges[badge]
  return (
    <Box direction="row" align="center">
      <BadgeSVG />
      <Paragraph margin={{ left: 'small' }}>{label}</Paragraph>
    </Box>
  )
}

export default Badge
