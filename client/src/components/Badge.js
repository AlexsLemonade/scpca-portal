import React, { useEffect, useState } from 'react'
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

export const Badge = ({ badge, label, className, children }) => {
  const BadgeSVG = badges[badge]
  const [id, setId] = useState('')

  useEffect(() => {
    setId(`${Math.random().toString(36).substr(2, 9)}-${Date.now()}`)
  }, [])

  return (
    <Box direction="row" align="center" className={className}>
      <Box width="24px">
        <BadgeSVG
          id={id}
          role="presentation"
          aria-hidden="true"
          focusable="false"
        />
      </Box>
      <Paragraph margin={{ left: 'small' }}>{label}</Paragraph>
      {children}
    </Box>
  )
}

export default Badge
