import React from 'react'
import { Text } from 'grommet'
import { InfoText } from 'components/InfoText'
import { Link } from 'components/Link'

export const InfoViewMyDataset = ({ newTab = false }) => {
  return (
    <InfoText>
      <Text>
        Some samples are in My Dataset.{' '}
        <Link href="/download" label="View My Dataset" newTab={newTab} />
      </Text>
    </InfoText>
  )
}

export default InfoViewMyDataset
