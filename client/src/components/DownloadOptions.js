import React from 'react'
import { FormField, Grid, Box, Select } from 'grommet'
import styled from 'styled-components'
import { DownloadOption } from 'components/DownloadOption'
import { useDownloadOptionsContext } from 'hooks/useDownloadOptionsContext'
import getReadableOptions from 'helpers/getReadableOptions'
import config from 'config'
import { HelpLink } from 'components/HelpLink'

const BoldFormField = styled(FormField)`
  label {
    font-weight: bold;
  }
`

export const DownloadOptions = ({ handleSelectFile }) => {
  const {
    modality,
    setModality,
    modalityOptions,
    format,
    setFormat,
    formatOptions,
    computedFile,
    resource
  } = useDownloadOptionsContext()

  return (
    <Grid columns={['auto']} gap="large" pad={{ bottom: 'medium' }}>
      <Box
        direction="row"
        alignContent="between"
        gap="large"
        pad={{ bottom: 'large' }}
        border={{ side: 'bottom', color: 'border-black', size: 'small' }}
      >
        <BoldFormField label="Modality">
          <Select
            options={getReadableOptions(modalityOptions)}
            labelKey="label"
            valueKey={{ key: 'value', reduce: true }}
            value={modality}
            onChange={({ value }) => setModality(value)}
          />
        </BoldFormField>
        <BoldFormField
          label={
            <HelpLink label="Data Format" link={config.links.whatDownloading} />
          }
        >
          <Select
            options={getReadableOptions(formatOptions)}
            labelKey="label"
            valueKey={{ key: 'value', reduce: true }}
            value={format}
            onChange={({ value }) => setFormat(value)}
          />
        </BoldFormField>
      </Box>
      <Box>
        {computedFile && (
          <DownloadOption
            resource={resource}
            computedFile={computedFile}
            handleSelectFile={handleSelectFile}
          />
        )}
      </Box>
    </Grid>
  )
}

export default DownloadOptions
