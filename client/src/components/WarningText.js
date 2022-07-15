import React from 'react'
import { Box, Paragraph } from 'grommet'
import { Icon } from 'components/Icon'
import { Link } from 'components/Link'

export const WarningText = ({
  lineBreak = true,
  link = '',
  linkLable = '',
  iconMargin = [0, 'medium', 0, 0],
  iconPad = [0, 'small', 0, 0],
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
      <Box
        margin={{
          top: iconMargin[0],
          right: iconMargin[1],
          bottom: iconMargin[2],
          left: iconMargin[3]
        }}
        pad={{
          top: iconPad[0],
          right: iconPad[1],
          bottom: iconPad[2],
          left: iconPad[3]
        }}
      >
        <Icon color="status-warning" size={iconSize} name="Warning" />
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
