import React, { useEffect, useState } from 'react'
import { Box, Text } from 'grommet'
import { config } from 'config'
import { api } from 'api'
import { useCopyToClipboard } from 'hooks/useCopyToClipboard'
import { useScPCAPortal } from 'hooks/useScPCAPortal'
import { Button } from 'components/Button'
import { HelpLink } from 'components/HelpLink'
import { Modal, ModalBody } from 'components/Modal'
import { Icon } from 'components/Icon'
import { CCDLDatasetDownloadToken } from 'components/CCDLDatasetDownloadToken'
import { portalWideDatasets } from 'config/ccdlDatasets'

const TokenModal = ({ dataset, showing, setShowing }) => {
  const modalTitle = `Copy Download Link for ${
    portalWideDatasets[dataset.ccdl_name]?.modalTitle
  }`
  return (
    <Modal title={modalTitle} showing={showing} setShowing={setShowing}>
      <ModalBody>
        <CCDLDatasetDownloadToken />
      </ModalBody>
    </Modal>
  )
}

export const CCDLDatasetCopyLinkButton = ({ dataset }) => {
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
  const [wantsLink, setWantsLink] = useState(false)

  const [, copyText] = useCopyToClipboard()
  const { token } = useScPCAPortal()
  const needsToken = !token

  const [tokenModalShowing, setTokenModalShowing] = useState(false)

  const isDisabled = !dataset?.computed_file

  const onClick = () => {
    if (!isDisabled) setWantsLink(true)
  }

  useEffect(() => {
    setState(states.unclicked)
    setDownloadLink(null)
    setWantsLink(false)
  }, [dataset])

  useEffect(() => {
    if (wantsLink && !token) setTokenModalShowing(true)
  }, [wantsLink, token])

  useEffect(() => {
    const asyncFetch = async () => {
      const downloadRequest = await api.ccdlDatasets.get(dataset.id, token)
      if (downloadRequest.isOk) {
        setDownloadLink(downloadRequest.response.download_url)
      }
    }

    if (!downloadLink && wantsLink && token) {
      asyncFetch()
    }
  }, [downloadLink, wantsLink, token])

  useEffect(() => {
    const asyncCopy = async () => {
      await copyText(downloadLink)
      setState(states.clicked)

      setTimeout(() => {
        setState(states.unclicked)
      }, 5000)
    }

    if (downloadLink && wantsLink) {
      asyncCopy()
      setWantsLink(false)
    }
  }, [downloadLink, wantsLink])

  return (
    <>
      <Box direction="row">
        <Button plain label={state.label} icon={state.icon} onClick={onClick} />
        <HelpLink link={config.links.what_copy_link} />
      </Box>
      {needsToken && (
        <TokenModal
          dataset={dataset}
          showing={tokenModalShowing}
          setShowing={setTokenModalShowing}
        />
      )}
    </>
  )
}
