import React from 'react'
import styled, { css } from 'styled-components'
import { Button } from 'grommet'
import { AnalyticsContext } from 'contexts/AnalyticsContext'

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

export const DonateButton = ({ yellow = false, label = 'Donate' }) => {
  const { trackDonate } = React.useContext(AnalyticsContext)
  const Component = yellow ? StyledButton : Button
  return (
    <Component
      href="https://www.ccdatalab.org/donate-link"
      target="_blank"
      label={label}
      primary
      onClick={trackDonate}
    />
  )
}

export default DonateButton
