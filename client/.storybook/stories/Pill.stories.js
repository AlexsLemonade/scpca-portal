import React from 'react'
import { Box, Paragraph } from 'grommet'
import { Pill, NumberPill } from 'components/Pill'

const numbers = [1, 10, 100, 1000, 1500, 3500, 10000, 25000, 255000, 15000000]

export default {
  title: 'Components/Pill'
}

export const DefaultPill = () => (
  <>
    <Box pad="medium">
      <Pill label="badge-label" />
    </Box>
    <Box pad="medium">
      <Pill label="Another Example" />
    </Box>
    <Box pad="medium">
      <Pill background="brand" color="white" label="Brand Example" />
    </Box>
  </>
)

export const DefaultNumberPill = () => (
  <>
    {numbers.map((number) => (
      <Box pad="medium" key={number}>
        <Box>
          <Paragraph>{number}</Paragraph>
          <NumberPill value={number} />
        </Box>
      </Box>
    ))}
  </>
)
