import React from 'react'
import { Box } from 'grommet'
import styled, { css } from 'styled-components'

const LoaderBox = styled(Box)`
  display: inline-flex;
  algin-item: center;
  justiy-content: center;
  position: relative;
  ${({ theme, width }) =>
    css`
      width: ${width}px;
      height: ${width}px;

      > div {
        border: ${width === 80 ? '8' : '4'}px solid
          ${theme.global.colors['alexs-deep-blue']};
        border-color: ${theme.global.colors['alexs-deep-blue']} transparent
          transparent transparent;
        border-radius: 50%;
        box-sizing: border-box;
        display: block;
        position: absolute;
        width: ${width}px;
        height: ${width}px;
        animation: loader 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;

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
  const loaderWidth = width === 'full' ? '80px' : `${parseInt(width, 10)}px`
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
