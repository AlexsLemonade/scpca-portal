import React from 'react'
import { useResponsive } from 'hooks/useResponsive'
import { Box, Paragraph, Markdown } from 'grommet'
import { Banner } from 'components/Banner'
import { Icon } from 'components/Icon'
import getTemplateLines from 'helpers/getTemplateLines'
import styled from 'styled-components'

// options does not honor wrapper override
const StyledMarkdown = styled(Markdown)`
  text-align: center;
`

export const EnvarBanner = ({ id = 'environment-variable-banner', width }) => {
  const lines = getTemplateLines(process.env.BANNER_CONTENT)
  const { responsive } = useResponsive()
  return (
    <Banner id={id} background="alexs-lemonade-tint-75" width={width}>
      <Box pad={{ vertical: 'large' }}>
        <Box
          direction={responsive('column', 'row')}
          align="center"
          justify="center"
          flex="grow"
          zIndex={2}
        >
          <Icon
            color="error"
            name="WarningNoFill"
            size="36px"
            aria-hidden="true"
          />
          <Box
            color="black"
            margin={{ left: 'medium' }}
          >
            {lines.map((content) => (
              <StyledMarkdown key={content}>{content}</StyledMarkdown>
            ))}
          </Box>
        </Box>
      </Box>
    </Banner>
  )
}

export default EnvarBanner
