import React, { useState } from 'react'
import { Box } from 'grommet'
import { Icon } from 'components/Icon'
import styled, { css } from 'styled-components'

export const Banner = ({
  bgColor = 'brand',
  fontColor = 'white',
  iconName,
  iconSize,
  children
}) => {
  const [showing, setShowing] = useState(true)
  const BannerBox = styled(Box)`
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    width: 100%;
    height: 56px;
    ${({ theme }) => css`
      background-color: ${theme.global.colors[bgColor] ||
      theme.global.colors.gradient[bgColor]};
      > div {
        align-item: center;
        align-self: center;
        display: flex;
        flex-direction: row;
        font-size: 21px;
        justify-content: center;
        &:first-child {
          flex: 1;
        }
        &:last-child {
          padding: 20px;
        }
        > svg + p,
        div + p {
          margin-left: 4px;
        }
        > p {
          color: ${theme.global.colors[fontColor]};
          font-size: 21px;
          > a {
            color: inherit;
            text-decoration: underline;
          }
        }
      }
    `}
  `

  return (
    <>
      {showing && (
        <BannerBox>
          <Box>
            {iconName && (
              <Icon name={iconName} size={iconSize} aria-hidden="true" />
            )}
            {children}
          </Box>
          <Box onClick={() => setShowing(false)}>
            <Icon name="Cross" size="16px" color={fontColor} />
          </Box>
        </BannerBox>
      )}
    </>
  )
}
export default Banner
