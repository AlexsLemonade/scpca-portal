import React from 'react'
import { Box, Stack, Text } from 'grommet'
import { Button } from 'components/Button'
import styled, { css } from 'styled-components'

const YellowButton = styled(Button)`
  ${({ theme }) =>
    css`
      border: none;
      background-color: ${theme.global.colors['alexs-lemonade']};
      color: ${theme.global.colors['black']};
      &:hover {
        background-color: ${theme.global.colors['alexs-lemonade-tint-40']};
        color: ${theme.global.colors['alexs-deep-blue']};
      }
    `}
`

export const MyDatasetButton = () => {
  const count = 53
  return (
    <Box direction='row'>
      <YellowButton
        href="/"
        label="My Dataset"
        primary
        badge={
          <Box
            background="alexs-lemonade"
            round
            pad="xsmall"
            border={{
              color: "alexs-deep-blue",
              size: "4px",
            }}>
            <Text size="small-flat">{count}</Text>
          </Box>
        }
      />
    </Box >
  )
}

export default MyDatasetButton
