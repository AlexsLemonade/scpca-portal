import React from 'react'
import { useResponsive } from 'hooks/useResponsive'
import { Box, Paragraph, Markdown } from 'grommet'
import { Banner } from 'components/Banner'
import { Icon } from 'components/Icon'
import getTemplateLines from 'helpers/getTemplateLines'

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
          <Paragraph
            color="black"
            margin={{ left: 'medium' }}
            textAlign="center"
          >
            {lines.map((content) => (
              <Markdown key={content}>{content}</Markdown>
            ))}
          </Paragraph>
        </Box>
      </Box>
    </Banner>
  )
}

export default EnvarBanner
