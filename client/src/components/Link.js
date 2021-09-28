import React from 'react'
import NextLink from 'next/link'
import { Anchor } from 'grommet'
import isExternalPath from 'helpers/isExternalPath'

export const Link = ({
  href,
  label,
  icon,
  as,
  children = '',
  color = 'brand'
}) => {
  return isExternalPath(href) ? (
    <Anchor
      target="_blank"
      color={color}
      href={href}
      label={label}
      icon={icon}
      as={as}
    >
      {children}
    </Anchor>
  ) : (
    <NextLink href={href}>
      <Anchor color={color} href={href} label={label} icon={icon} as={as}>
        {children}
      </Anchor>
    </NextLink>
  )
}

export default Link
