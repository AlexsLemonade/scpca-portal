import React from 'react'
import { useCellbrowserIframe } from 'hooks/useCellbrowserIframe'
import styled from 'styled-components'
import { Box, Text, Stack } from 'grommet'
import { Loader } from './Loader'

const Iframe = styled.iframe`
  padding: 35px 0 0 0;
  height: calc(100vh - 147px);
  width: 100vw;
  max-width: 100%;
  visibility: ${({ isVisible }) => (isVisible ? 'visible' : 'hidden')};
  opacity: ${({ isVisible }) => (isVisible ? '100%' : '0%')};
  transition: opacity 0.25s ease-in-out;
`

export const CellbrowserIframe = () => {
  const { isIframeReady, setIsIframeLoaded, iframeRef, status } =
    useCellbrowserIframe()

  return (
    <Stack anchor="center">
      <Iframe
        ref={iframeRef}
        src="/api/cellbrowser/proxy/"
        isVisible={isIframeReady}
        onLoad={() => setIsIframeLoaded(true)}
      />
      {!isIframeReady && (
        <Box gap="large">
          <Loader />
          <Text>{status}</Text>
        </Box>
      )}
    </Stack>
  )
}

export default CellbrowserIframe
