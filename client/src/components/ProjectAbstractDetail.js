import React from 'react'
import { Paragraph } from 'grommet'

export const ProjectAbstractDetail = ({ abstract }) =>
  abstract.split('\n').map((line) => <Paragraph>{line}</Paragraph>)
