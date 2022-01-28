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

export const Badge = ({ badge, label, className }) => {
  const BadgeSVG = badges[badge]
  return (
    <Box direction="row" align="center" className={className}>
      <Box width="24px">
        <BadgeSVG />
      </Box>
      <Paragraph margin={{ left: 'small' }}>{label}</Paragraph>
    </Box>
  )
}

export default Badge
