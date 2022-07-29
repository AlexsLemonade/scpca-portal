import React from 'react'
import { Box, Paragraph } from 'grommet'
import styled from 'styled-components'
import { abbreviateNumbers } from 'helpers/formatNumbers'

export const Pill = ({
  background = 'alexs-lemonade-tint-75',
  color = 'brand',
  textColor = 'text',
  textSize = 'medium',
  label = '',
  bullet = true
}) => {
  return (
    <Box
      background={background}
      direction="row"
      round="12px"
      height="24px"
      width="auto"
      as="span"
      alignSelf="start"
      pad={{ vertical: '0', horizontal: '8px' }}
    >
      {bullet && (
        <Box
          width="8px"
          height="8px"
          round="100%"
          background={color}
          alignSelf="center"
          as="span"
          margin={{ right: '4px' }}
        />
      )}

      <Paragraph
        color={textColor}
        size={textSize}
        responsive={false}
        alignSelf="center"
        margin="none"
      >
        {label}
      </Paragraph>
    </Box>
  )
}

const P = styled(Paragraph)`
  margin-bottom: 2px;
`

export const NumberPill = ({
  background = 'brand',
  color = 'black-tint-80',
  value = ''
}) => {
  return (
    <Box
      background={background}
      direction="row"
      round="8px"
      height="16px"
      width={{ min: '16px' }}
      as="span"
      alignSelf="start"
      pad={{ vertical: '0px', horizontal: '4px' }}
    >
      <P
        color={color}
        size="small"
        responsive={false}
        alignSelf="center"
        margin="none"
      >
        {abbreviateNumbers(value)}
      </P>
    </Box>
  )
}

export default Pill
