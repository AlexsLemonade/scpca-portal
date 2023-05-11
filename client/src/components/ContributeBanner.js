import React from 'react'
import { Box, Heading, Paragraph } from 'grommet'
import { Banner } from 'components/Banner'
import { Button } from 'components/Button'

export const ContributeBanner = () => {
  return (
    <Banner
      id="contribute-banner"
      background="alexs-lemonade-tint-60"
      fullWidth={false}
      elevation="large"
    >
      <Box align="center" pad="medium">
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
              The ScPCA Portal is expanding! We are now accepting submissions
              from pediatric cancer researchers with existing single-cell
              datasets. Eligible researchers may receive a small grant for their
              submission.
            </Paragraph>
            <Button
              href="/contribute"
              label="Data Contribution Guidelines"
              primary
            />
          </Box>
        </Box>
      </Box>
    </Banner>
  )
}

export default ContributeBanner
