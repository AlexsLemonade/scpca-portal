import React, { useState } from 'react'
import { Box, Heading, Paragraph } from 'grommet'
import { Button } from 'components/Button'
import { Icon } from 'components/Icon'

export const ContributeBanner = () => {
  const [show, setShow] = useState(true)

  if (!show) return null

  return (
    <Box
      background="alexs-lemonade-tint-60"
      elevation="large"
      align="center"
      pad="medium"
      style={{ zIndex: 1 }} // prevents Header's box shadow from showing on top
    >
      <Box direction="row" justify="between">
        <Box
          align="center"
          justify="center"
          width="xlarge"
          margin={{ top: 'medium' }}
        >
          <Heading level={2} size="small">
            Contribute your data to the ScPCA Portal
          </Heading>
          <Paragraph
            margin="medium"
            textAlign="center"
            style={{ width: '680px' }} // sets the fix width to preserve the UI layout
          >
            The ScPCA Portal is expanding! We are now accepting submissions from
            pediatric cancer researchers with existing single-cell datasets.
            Eligible researchers may receive a small grant for their submission.
          </Paragraph>
          <Button
            href="/contribute"
            label="Data Contribution Guidelines"
            primary
          />
        </Box>
        <Box onClick={() => setShow(false)}>
          <Icon name="Cross" size="16px" color="black" />
        </Box>
      </Box>
    </Box>
  )
}

export default ContributeBanner
