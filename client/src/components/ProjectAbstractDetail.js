import React from 'react'
import { Paragraph } from 'grommet'

export const ProjectAbstractDetail = ({ abstract }) =>
  abstract
    .split('\\n')
    .map((line, i) => (
      <Paragraph key={line} margin={{ top: i && 'small' }}>{line}</Paragraph>
    ))
