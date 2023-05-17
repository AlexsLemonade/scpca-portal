import React from 'react'
import { Text } from 'grommet'

export const ProjectAbstractDetail = ({ abstract }) => {
  const content = abstract.split('\\n')

  if (content.length === 1) return content

  return content.map((line, i) => (
    <Text
      key={line}
      margin={{ top: i ? 'small' : 'none' }}
      style={{ display: 'block' }}
    >
      {line}
    </Text>
  ))
}
