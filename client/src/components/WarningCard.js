import React from 'react'
import { Box, Text } from 'grommet'
import { CardBandLarge } from 'components/Band'
import { WarningText } from 'components/WarningText'

export const WarningCard = ({ label, children }) => {
  return (
    <CardBandLarge
      align="center"
      elevation="small"
      pad={{ top: 'xxlarge' }}
      width="100%"
    >
      <Box margin={{ bottom: 'medium' }}>
        <WarningText
          iconColor="error"
          iconNoFill
          iconMargin="none"
          iconSize="24px"
          text={
            <Text color="error" size="24px" weight="bold">
              {label}
            </Text>
          }
        />
      </Box>
      {children}
    </CardBandLarge>
  )
}

export default WarningCard
