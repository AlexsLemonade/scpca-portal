import React, { useEffect, useState } from 'react'
import { Box, Text } from 'grommet'
import styled, { css } from 'styled-components'

const ArrowIcon = styled(Box)`
  ${({ theme }) => css`
    border: 1px solid ${theme.global.colors.brand.light};
    &::before {
      border: 1px solid ${theme.global.colors.brand.light};
    }
  `}
  border-width: 1px 1px 0 0;
  margin: 0 calc(50% - 4px);
  height: 6px;
  width: 6px;
  position: relative;
  transform: rotate(-45deg);
  &::before {
    content: '';
    border-radius: 50%;
    width: 24px;
    height: 24px;
    position: absolute;
    left: -8px;
    top: -12px;
  }
`

const ButtonBody = styled(Box)`
  box-shadow: none;
`

const ButtonContainer = styled(Box)`
  ${({ show }) => css`
    display: ${show ? 'block' : 'none'};
  `}
  position: fixed;
  bottom: 5vh;
  right: 5vw;
  z-index: 10;
`

export const BackToTopButton = () => {
  const offset = 1000
  const isWindow = typeof window !== 'undefined'

  const [show, setShow] = useState(false)

  const handleClick = () => window.scrollTo({ top: 0, behavior: 'smooth' })

  useEffect(() => {
    const toggleShow = () => {
      const scrolled = document.documentElement.scrollTop
      if (scrolled > offset) {
        setShow(true)
      } else if (scrolled <= offset) {
        setShow(false)
      }
    }

    if (isWindow) {
      window.addEventListener('scroll', toggleShow)
    }

    return () => {
      if (isWindow) {
        window.removeEventListener('scroll', toggleShow)
      }
    }
  }, [isWindow])

  return (
    <ButtonContainer
      animation={{ type: show ? 'fadeIn' : 'fadeOut', duration: 500 }}
      background="black-tint-95"
      elevation="xlarge"
      round="2px"
      show={show}
    >
      <ButtonBody
        role="button"
        pad={{ top: '20px', bottom: 'xsmall', horizontal: 'small' }}
        onClick={handleClick}
      >
        <ArrowIcon />
        <Text
          color="brand"
          margin={{ top: 'small' }}
          size="small"
          weight="bold"
        >
          Back to Top
        </Text>
      </ButtonBody>
    </ButtonContainer>
  )
}

export default BackToTopButton
