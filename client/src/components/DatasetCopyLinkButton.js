import React, { useEffect, useState } from 'react'
import { Box, Text } from 'grommet'
import { config } from 'config'
import { useCopyToClipboard } from 'hooks/useCopyToClipboard'
import { Button } from 'components/Button'
import { HelpLink } from 'components/HelpLink'
import { Icon } from 'components/Icon'

export const DatasetCopyLinkButton = ({ dataset, disabled = false }) => {
  const [, copyText] = useCopyToClipboard()

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
  const [wantsLink, setWantsLink] = useState(false)

  const buttonStyle = disabled
    ? {
        opacity: 0.6,
        cursor: 'not-allowed'
      }
    : {}

  const handleCopy = () => {
    if (!disabled) setWantsLink(true)
  }

  useEffect(() => {
    const asyncCopy = async () => {
      await copyText(dataset.download_url)
      setState(states.clicked)
    }

    if (wantsLink) {
      asyncCopy()
      setWantsLink(false)
    }
  }, [wantsLink])

  return (
    <Box direction="row">
      <Button
        plain
        label={state.label}
        icon={state.icon}
        disabled={disabled}
        style={buttonStyle}
        onClick={handleCopy}
      />
      <HelpLink link={config.links.what_copy_link} />
    </Box>
  )
}
