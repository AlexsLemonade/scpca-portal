import React from 'react'
import { Box, Text } from 'grommet'
import { Button } from 'components/Button'
import styled, { css } from 'styled-components'

const YellowButton = styled(Button)`
  ${({ theme }) =>
    css`
      border: none;
      background-color: ${theme.global.colors['alexs-lemonade']};
      color: ${theme.global.colors.black};
      &:hover {
        background-color: ${theme.global.colors['alexs-lemonade-tint-40']};
        color: ${theme.global.colors['alexs-deep-blue']};
      }
    `}
`
// TODO: Add getTotalSampleCount helper to useMyDataset when building the download page
export const MyDatasetButton = () => {
  const count = 0
  return (
    <Box direction="row">
      <YellowButton
        href="/download"
        label="My Dataset"
        primary
        badge={
          <Box
            background="alexs-lemonade"
            round
            pad="xsmall"
            border={{
              color: 'alexs-deep-blue',
              size: '4px'
            }}
          >
            <Text size="small-flat">{count}</Text>
          </Box>
        }
      />
    </Box>
  )
}

export default MyDatasetButton
