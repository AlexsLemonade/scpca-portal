import React, { useEffect, useRef, useState } from 'react'
import { Anchor, Box, Grid, Heading, Paragraph, Text, TextInput } from 'grommet'
import { config } from 'config'
import { api } from 'api'
import { useCopyToClipboard } from 'hooks/useCopyToClipboard'
import { useScPCAPortal } from 'hooks/useScPCAPortal'
import { useResponsive } from 'hooks/useResponsive'
import { Button } from 'components/Button'
import { HelpLink } from 'components/HelpLink'
import { Modal, ModalBody } from 'components/Modal'
import { Icon } from 'components/Icon'
import { CCDLDatasetDownloadToken } from 'components/CCDLDatasetDownloadToken'

const TokenModal = ({ showing, setShowing }) => {
  const modalTitle = 'Accept terms of service'

  return (
    <Modal title={modalTitle} showing={showing} setShowing={setShowing}>
      <ModalBody>
        <CCDLDatasetDownloadToken />
      </ModalBody>
    </Modal>
  )
}

export const DatasetCopyLinkButton = ({ dataset }) => {
  const { responsive } = useResponsive()
  const inputRef = useRef(null)

  const states = {
    unclicked: {
      label: 'Copy Link',
      icon: null
    },
    clicked: {
      label: <Text color="success">Copied to clipboard!</Text>,
      icon: <Icon color="success" name="Check" />,
      plain: true
    }
  }

  const [state, setState] = useState(states.unclicked)
  const [downloadLink, setDownloadLink] = useState(dataset.download_url)
  const [isGenerateClicked, setIsGenerateClicked] = useState(false)

  const [, copyText] = useCopyToClipboard()
  const { token } = useScPCAPortal()

  const isCCDL = !!dataset?.ccdl_name
  const isDisabled = !dataset?.computed_file

  const handleCopy = () => {
    if (isDisabled) return
    copyText(downloadLink)
    setState(states.clicked)
  }

  const handleInputClick = () => {
    inputRef.current?.select()
  }

  useEffect(() => {
    setState(states.unclicked)
    setDownloadLink(null)
    setIsGenerateClicked(false)
  }, [dataset])

  useEffect(() => {
    const asyncFetch = async () => {
      const downloadRequest = isCCDL
        ? await api.ccdlDatasets.get(dataset.id, token)
        : await api.datasets.get(dataset.id, token)
      if (downloadRequest.isOk) {
        setDownloadLink(downloadRequest.response.download_url)
      }
    }

    if (!downloadLink && isGenerateClicked && token) {
      asyncFetch()
    }
  }, [downloadLink, isGenerateClicked, token])

  useEffect(() => {
    const asyncCopy = async () => {
      await copyText(downloadLink)
    }

    if (downloadLink && isGenerateClicked) {
      asyncCopy()
      setIsGenerateClicked(false)
    }
  }, [downloadLink, isGenerateClicked])

  return (
    <Box
      border={{ side: 'top', color: 'border-black', size: 'small' }}
      pad={{ top: 'large' }}
    >
      <Heading level={5}>Download link for command line tools</Heading>
      <Paragraph margin={{ bottom: 'medium' }}>
        Download data using tools like <Text color="error">wget</Text> or{' '}
        <Text color="error">curl</Text>.{' '}
        <Anchor
          href={config.links.how_to_use_cli_link_to_download}
          target="_blank"
          label="Learn more"
        />
      </Paragraph>

      {!downloadLink ? (
        <>
          <Box align="start">
            <Button
              label="Generate"
              disabled={isDisabled}
              onClick={() => setIsGenerateClicked(true)}
            />
          </Box>
          {isGenerateClicked && !token && (
            <TokenModal showing setShowing={setIsGenerateClicked} />
          )}
        </>
      ) : (
        <Grid
          columns={responsive('1', ['2/3', '1/3'])}
          gap={responsive('', 'medium')}
        >
          <Box>
            <TextInput
              ref={inputRef}
              value={downloadLink ?? ''}
              readOnly
              onClick={handleInputClick}
            />
          </Box>
          <Box direction="row">
            <Button
              plain={state.plain}
              label={state.label}
              icon={state.icon}
              disabled={isDisabled}
              onClick={handleCopy}
            />
            <HelpLink link={config.links.what_copy_link} />
          </Box>
        </Grid>
      )}
    </Box>
  )
}

export default DatasetCopyLinkButton
