import React from 'react'
import styled, { css } from 'styled-components'
import { Button } from 'grommet'

export const StyledButton = styled(Button)`
  ${({ theme }) =>
    css`
      background-color: ${theme.global.colors['alexs-lemonade']};
      color: ${theme.global.colors['alexs-deep-blue']};
      &:hover {
        background-color: ${theme.global.colors['alexs-lemonade-tint-40']};
        color: ${theme.global.colors['alexs-deep-blue']};
      }
    `}
`

export const DonateButton = () => (
  <StyledButton
    href="https://www.alexslemonade.org/contribute/7?restrict=Childhood%20Cancer%20Data%20Lab"
    target="_blank"
    label="Donate"
  />
)

export default DonateButton
