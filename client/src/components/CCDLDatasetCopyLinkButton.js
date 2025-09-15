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
import { portalWideDatasets } from 'config/ccdlDatasetDownloadModal'

const TokenModal = ({ dataset, showing, setShowing }) => {
  const modalTitle = `Copy Download Link for ${
    portalWideDatasets[dataset.ccdl_name]?.title
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

  const [showing, setShowing] = useState(false)

  const onClick = async () => {
    setWantsLink(true)
    if (!token) setShowing(true)
  }

  useEffect(() => {
    setState(states.unclicked)
    setDownloadLink(null)
  }, [dataset])

  useEffect(() => {
    const asyncFetchAndCopy = async () => {
      let link = downloadLink
      if (!downloadLink) {
        const downloadRequest = await api.ccdlDatasets.get(dataset.id, token)
        if (downloadRequest.isOk) {
          link = downloadRequest.response.download_url
          setDownloadLink(link)
        }
      }
      await copyText(link)
      setState(states.clicked)
    }

    if (wantsLink && token) {
      asyncFetchAndCopy()
      setWantsLink(false)
    }
  }, [wantsLink, token])

  return (
    <>
      <Box direction="row">
        <Button plain label={state.label} icon={state.icon} onClick={onClick} />
        <HelpLink link={config.links.what_copy_link} />
      </Box>
      {!token && (
        <TokenModal
          dataset={dataset}
          showing={showing}
          setShowing={setShowing}
        />
      )}
    </>
  )
}
