import React from 'react'
import { Box, Text } from 'grommet'
import { useRouter } from 'next/router'
import { Button } from 'components/Button'
import EmptyDatasetImg from '../images/empty-dataset.svg'

export const DatasetEmpty = () => {
  const { push } = useRouter()

  return (
    <Box align="center" gap="medium">
      <EmptyDatasetImg />
      <Text size="xxlarge">Your dataset is empty!</Text>
      <Button
        aria-label="Browse and Add Samples"
        label="Browse and Add Samples"
        primary
        onClick={() => push('/projects')}
      />
    </Box>
  )
}
export default DatasetEmpty
