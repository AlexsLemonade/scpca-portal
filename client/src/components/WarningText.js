import React from 'react'
import { Box, Paragraph } from 'grommet'
import { Icon } from 'components/Icon'
import { Link } from 'components/Link'

export const WarningText = ({
  lineBreak = true,
  link = '',
  linkLabel = '',
  iconColor = 'status-warning',
  iconMargin = { right: 'medium' },
  iconName = 'Warning',
  iconPad = { right: 'small' },
  iconSize = '16px',
  text = '',
  newTab = false,
  margin = { top: 'small', bottom: 'medium' },
  children
}) => {
  return (
    <Box align="center" direction="row" margin={margin}>
      <Box margin={iconMargin} pad={iconPad}>
        <Icon color={iconColor} size={iconSize} name={iconName} />
      </Box>
      <Paragraph>
        {text} {lineBreak && <br />}
        {link && <Link label={linkLabel} href={link} newTab={newTab} />}
      </Paragraph>
      {children}
    </Box>
  )
}

export default WarningText
