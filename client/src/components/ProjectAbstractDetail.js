import React from 'react'
import { Paragraph } from 'grommet'

export const ProjectAbstractDetail = ({ label }) =>
  label.split('\n').map((line) => <Paragraph>{line}</Paragraph>)
