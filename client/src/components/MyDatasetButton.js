import React, { useEffect, useState } from 'react'
import { Box, Text } from 'grommet'
import { useRouter } from 'next/router'
import { useMyDataset } from 'hooks/useMyDataset'
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

export const MyDatasetButton = () => {
  const { push } = useRouter()
  const { myDataset, getDataset } = useMyDataset()
  const { total_sample_count: count = 0 } = myDataset

  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchDataset = async () => {
      await getDataset()
      setLoading(false)
    }

    if (loading) fetchDataset()
  }, [loading, myDataset])

  return (
    <Box direction="row">
      <YellowButton
        label="My Dataset"
        primary
        badge={
          <Box
            width={{ min: '32px' }}
            height="32px"
            align="center"
            justify="center"
            background="alexs-lemonade"
            border={{
              color: 'alexs-deep-blue',
              size: '4px'
            }}
            pad="xsmall"
            round
          >
            <Text size="small-flat">{count}</Text>
          </Box>
        }
        onClick={() => push('/download')}
      />
    </Box>
  )
}

export default MyDatasetButton
