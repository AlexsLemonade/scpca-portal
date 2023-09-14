import React from 'react'
import { Box, Paragraph } from 'grommet'
import { Icon } from 'components/Icon'
import { Link } from 'components/Link'

export const WarningText = ({
  lineBreak = true,
  link = '',
  linkLable = '',
  iconColor = 'status-warning',
  iconMargin = { right: 'medium' },
  iconPad = { right: 'small' },
  iconSize = '16px',
  text = '',
  children
}) => {
  return (
    <Box
      align="center"
      direction="row"
      margin={{ top: 'small', bottom: 'medium' }}
    >
      <Box margin={iconMargin} pad={iconPad}>
        <Icon color={iconColor} size={iconSize} name="Warning" />
      </Box>
      <Paragraph>
        {text} {lineBreak && <br />}
        {link && <Link label={linkLable} href={link} />}
        {children}
      </Paragraph>
    </Box>
  )
}

export default WarningText
