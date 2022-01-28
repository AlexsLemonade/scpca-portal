import React from 'react'
import { Box } from 'grommet'
import styled, { css } from 'styled-components'

const LoaderBox = styled(Box)`
  display: inline-block;
  position: relative;
  ${({ theme, width }) =>
    css`
      width: ${width}px;
      height: ${width}px;

      > div {
        box-sizing: border-box;
        display: block;
        position: absolute;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%);
        width: ${width}px;
        height: ${width}px;
        margin: 8px;
        border: ${width === 80 ? '8' : '4'}px solid
          ${theme.global.colors['alexs-deep-blue']};
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
export const Loader = ({ width = 'full', pad = { verical: 'large' } }) => {
  const loaderWidth = width === 'full' ? 80 : parseInt(width, 10)
  return (
    <Box width={width} align="center" justify="center" pad={pad}>
      <LoaderBox width={loaderWidth}>
        <Box />
        <Box />
        <Box />
        <Box />
      </LoaderBox>
    </Box>
  )
}
