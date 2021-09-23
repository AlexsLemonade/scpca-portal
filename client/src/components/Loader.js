import React from 'react'
import { Box } from 'grommet'
import styled, { css } from 'styled-components'

const LoaderBox = styled(Box)`
  display: inline-block;
  position: relative;
  width: 80px;
  height: 80px;
  ${({ theme }) =>
    css`
      > div {
        box-sizing: border-box;
        display: block;
        position: absolute;
        width: 64px;
        height: 64px;
        margin: 8px;
        border: 8px solid ${theme.global.colors['alexs-deep-blue']};
        border-radius: 50%;
        animation: loader 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
        border-color: ${theme.global.colors['alexs-deep-blue']} transparent
          transparent transparent;

        &:nth-child(1) {
          animation-delay: -0.45s;
        }

        &:nth-child(2) {
          animation-delay: -0.3s;
        }

        &:nth-child(3) {
          animation-delay: -0.15s;
        }
      }
    `}
  @keyframes loader {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
`
export const Loader = () => (
  <Box width="full" align="center" justify="center" pad={{ vertical: 'large' }}>
    <LoaderBox>
      <Box />
      <Box />
      <Box />
      <Box />
    </LoaderBox>
  </Box>
)
