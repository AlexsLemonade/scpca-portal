import { Box } from 'grommet'
import styled, { css } from 'styled-components'

export const HeroBand = styled(Box)`
  ${({ theme }) => css`
    background-image: linear-gradient(
        5deg,
        transparent 61%,
        ${theme.global.colors['alexs-light-blue-tint-60']} 61.1%,
        ${theme.global.colors['alexs-light-blue-tint-60']} 80%,
        transparent 80.1%
      ),
      linear-gradient(
        -5deg,
        transparent 61%,
        ${theme.global.colors['alexs-lemonade-tint-75']} 61.1%,
        ${theme.global.colors['alexs-lemonade-tint-75']} 84%,
        transparent 84.1%
      );
  `}
`

export const HeroBandReversed = styled(Box)`
  ${({ theme }) => css`
    background-image: linear-gradient(
        -5deg,
        transparent 61%,
        ${theme.global.colors['alexs-lemonade-tint-75']} 61.5%,
        ${theme.global.colors['alexs-lemonade-tint-75']} 84%,
        transparent 84.5%
      ),
      linear-gradient(
        5deg,
        transparent 61%,
        ${theme.global.colors['alexs-light-blue-tint-20']} 61.5%,
        ${theme.global.colors['alexs-light-blue-tint-20']} 84%,
        transparent 84.5%
      );
  `}
`

export const CardBand = styled(Box)`
  ${({ theme }) => css`
    background-image: linear-gradient(
        175deg,
        ${theme.global.colors['alexs-light-blue-tint-60']} 10%,
        transparent 10.3%
      ),
      linear-gradient(
        -175deg,
        ${theme.global.colors['alexs-lemonade-tint-75']} 10%,
        transparent 10.3%
      );
  `}
`

export const CardBandLarge = styled(Box)`
  ${({ theme }) => css`
    background-image: linear-gradient(
        177.8deg,
        ${theme.global.colors['alexs-light-blue-tint-40']} 15%,
        transparent 15.5%
      ),
      linear-gradient(
        -177.8deg,
        ${theme.global.colors['alexs-lemonade-tint-75']} 20%,
        transparent 20.5%
      );
  `}
`

export const FooterBand = styled(Box)`
  ${({ theme }) => css`
    background-image: linear-gradient(
        -0.6deg,
        transparent 92%,
        ${theme.global.colors['alexs-light-blue-tint-40']} 92.1%,
        ${theme.global.colors['alexs-light-blue-tint-40']} 97.5%,
        transparent 97.6%
      ),
      linear-gradient(
        -1deg,
        transparent 93%,
        ${theme.global.colors['alexs-light-blue']} 93%,
        ${theme.global.colors['alexs-light-blue']} 100%
      ),
      linear-gradient(
        1deg,
        transparent 90%,
        ${theme.global.colors['alexs-lemonade-tint-75']} 90%
      ),
      linear-gradient(0deg, #fdfdfd 0%, #edf7fd 100%);
  `}
`

export const HeroBandPortalWide = styled(Box)`
  ${({ theme }) => css`
    background-image: linear-gradient(
        -3deg,
        transparent 42%,
        ${theme.global.colors['alexs-light-blue']} 42.5%,
        ${theme.global.colors['alexs-light-blue']} 72%,
        transparent 72.5%
      ),
      linear-gradient(
        3deg,
        transparent 42%,
        ${theme.global.colors['alexs-lemonade-tint-75']} 42.5%,
        ${theme.global.colors['alexs-lemonade-tint-75']} 72%,
        transparent 72.5%
      );
  `}
`
