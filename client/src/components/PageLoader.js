import React from 'react'
import { delay } from 'helpers/delay'
import { Box } from 'grommet'
import styled, { css } from 'styled-components'

const ProgressBar = styled(Box)`
  position: relative;
  width: 100%;
  height: 100%;
  transform: translate(0, -100%);
`

const Progress = styled(Box)`
  background: white;
  position: absolute;
  left: 0;
  bottom: 0;
  width: 100%;

  ${({ theme }) => css`
    height: ${theme.global.borderSize.medium};
  `}

  div {
    height: inherit;

    ${({ theme, progress }) => css`
      background-color: ${theme.global.colors['border-yellow']};
      top: ${theme.global.borderSize.medium};
      width: ${progress}%;
      transition: width ${progress === 20 ? '0s' : '0.1s'} ease-out;
    `}

    ${({ error, theme }) =>
      error &&
      css`
        background-color: ${theme.global.colors.error};
      `}
  }
`

export const PageLoader = ({ router }) => {
  const [progress, setProgress] = React.useState(0)
  const [error, setError] = React.useState(false)

  React.useEffect(() => {
    const routeChangeStart = async () => {
      setProgress(20)
      await delay(250)
      setProgress(80)
    }
    const routeChangeComplete = async () => {
      await delay(250)
      setProgress(100)
      await delay(500)
    }
    const routeChangeError = async () => {
      setError(true)
      await delay(500)
      setProgress(100)
      setError(false)
      await delay(100)
    }

    router.events.on('routeChangeStart', routeChangeStart)
    router.events.on('routeChangeComplete', routeChangeComplete)
    router.events.on('routeChangeError', routeChangeError)
    setProgress(100)

    return () => {
      router.events.on('routeChangeStart', routeChangeStart)
      router.events.on('routeChangeComplete', routeChangeComplete)
      router.events.on('routeChangeError', routeChangeError)
    }
  }, [router.events])

  return (
    <ProgressBar>
      <Progress error={error} progress={progress}>
        <Box />
      </Progress>
    </ProgressBar>
  )
}

export default PageLoader
