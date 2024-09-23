import React from 'react'
import { useEffect, useState } from 'react'
import { Box } from 'grommet'
import { config } from 'config'
import { api } from 'api'
import { useCopyToClipboard } from 'hooks/useCopyToClipboard'
import { useScPCAPortal } from 'hooks/useScPCAPortal'
import { Button } from 'components/Button'
import { HelpLink } from 'components/HelpLink'
import { Icon } from 'components/Icon'

export const CopyLinkButton = ({computedFile}) => {
  const states = {
    unclicked:  {
      label: "Copy Download Link",
      icon: <Icon name="Copy" />,
      color: 'brand',
    },
    clicked: {
      label: "Copied to clipboard!",
      icon: <Icon name="Check" color="success" />,
      color: 'success',
    }
  }

  const [state, setState] = useState(states.unclicked)
  const [downloadLink, setDownloadLink] = useState(null)

  const copyText = useCopyToClipboard()
  const { token } = useScPCAPortal()

  const getDownloadLink = async () => {
    const downloadRequest = await api.computedFiles.get(
      computedFile.id,
      token
    )

    if (downloadRequest.isOk) {
      setDownloadLink(downloadRequest.response.download_url)
    }
  }

  const onClick = async () => {
    if (downloadLink) {
      await copyText(downloadLink)
      setState(states.clicked)
    }
    else {
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
    <Box
      direction='row'
    >
      <Button
        plain
        label={state.label}
        icon={state.icon}
        color={state.color}
        onClick={onClick}
      />
      <HelpLink
        link={config.links.what_copy_link}
      />
    </Box>
  )
}
