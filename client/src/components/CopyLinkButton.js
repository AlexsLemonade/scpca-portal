import React, { useEffect, useState } from 'react'
import { Box, Text } from 'grommet'
import { config } from 'config'
import { api } from 'api'
import { useCopyToClipboard } from 'hooks/useCopyToClipboard'
import { useScPCAPortal } from 'hooks/useScPCAPortal'
import { Button } from 'components/Button'
import { HelpLink } from 'components/HelpLink'
import { Icon } from 'components/Icon'

export const CopyLinkButton = ({ computedFile }) => {
  const states = {
    unclicked: {
      label: <Text color="brand">Copy Download Link</Text>,
      icon: <Icon name="Copy" />
    },
    clicked: {
      label: <Text color="success">Copied to clipboard!</Text>,
      icon: <Icon color="success" name="Check" />
    }
  }

  const [state, setState] = useState(states.unclicked)
  const [downloadLink, setDownloadLink] = useState(null)

  const [, copyText] = useCopyToClipboard()
  const { token } = useScPCAPortal()

  const getDownloadLink = async () => {
    const downloadRequest = await api.computedFiles.get(computedFile.id, token)

    if (downloadRequest.isOk) {
      setDownloadLink(downloadRequest.response.download_url)
    }
  }

  const onClick = async () => {
    if (downloadLink) {
      await copyText(downloadLink)
      setState(states.clicked)
    } else {
      getDownloadLink()
    }
  }

  useEffect(() => {
    const asyncCopy = async () => {
      await copyText(downloadLink)
      setState(states.clicked)
    }
    if (downloadLink) asyncCopy()
  }, [downloadLink])

  return (
    <Box direction="row">
      <Button plain label={state.label} icon={state.icon} onClick={onClick} />
      <HelpLink link={config.links.what_copy_link} />
    </Box>
  )
}
