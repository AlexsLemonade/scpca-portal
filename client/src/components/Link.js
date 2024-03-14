import React from 'react'
import NextLink from 'next/link'
import { Anchor } from 'grommet'
import { isExternalPath } from 'helpers/isExternalPath'
import styled from 'styled-components'

const LinkAnchor = styled(Anchor)`
  ${({ underline }) =>
    underline &&
    `
      text-decoration: underline;
    `}
`

export const Link = ({
  href,
  label,
  icon,
  as,
  children = '',
  color = 'brand',
  newTab = false,
  underline = false
}) => {
  return isExternalPath(href) || newTab ? (
    <LinkAnchor
      target="_blank"
      color={color}
      href={href}
      label={label}
      icon={icon}
      as={as}
      underline={underline}
    >
      {children}
    </LinkAnchor>
  ) : (
    <NextLink href={href} legacyBehavior>
      <LinkAnchor
        color={color}
        href={href}
        label={label}
        icon={icon}
        as={as}
        underline={underline}
      >
        {children}
      </LinkAnchor>
    </NextLink>
  )
}

export default Link
