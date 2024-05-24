import React from 'react'
import { FormField, Grid, Box, Select } from 'grommet'
import { config } from 'config'
import { useDownloadOptionsContext } from 'hooks/useDownloadOptionsContext'
import { useResponsive } from 'hooks/useResponsive'
import { getReadableOptions } from 'helpers/getReadableOptions'
import { CheckBoxMergedObjects } from 'components/CheckBoxMergedObjects'
import { CheckBoxExcludeMultiplexed } from 'components/CheckBoxExcludeMultiplexed'
import { DownloadOption } from 'components/DownloadOption'
import { HelpLink } from 'components/HelpLink'

const FormField = ({ label, selectWidth = 'auto', children }) => {
  const { responsive } = useResponsive()

  return (
    <Box
      direction={responsive('column', 'row')}
      align={responsive('start', 'center')}
    >
      <Box pad={{ right: 'medium' }}>{label}</Box>
      <Box width={{ max: selectWidth }}>{children}</Box>
    </Box>
  )
}

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

  const { has_multiplexed_data: hasMultiplexed } = resource
  const { responsive } = useResponsive()

  return (
    <Grid columns={['auto']} pad={{ bottom: 'medium' }}>
      <Heading level="3" size="small">
        Download Options
      </Heading>
      <Box
        border={{ side: 'bottom', color: 'border-black', size: 'small' }}
        margin={{ bottom: 'large' }}
        pad={{ vertical: 'large' }}
      >
        <Box
          direction={responsive('column', 'row')}
          alignContent="between"
          gap="large"
          pad={{ bottom: 'large' }}
        >
          <FormField label="Modality" selectWidth="116px">
            <Select
              options={getReadableOptions(modalityOptions)}
              labelKey="label"
              valueKey={{ key: 'value', reduce: true }}
              value={modality}
              onChange={({ value }) => setModality(value)}
            />
          </FormField>
          <FormField
            label={
              <HelpLink
                label="Data Format"
                link={config.links.what_downloading}
              />
            }
            selectWidth="200px"
          >
            <Select
              options={getReadableOptions(formatOptions)}
              labelKey="label"
              valueKey={{ key: 'value', reduce: true }}
              value={format}
              onChange={({ value }) => setFormat(value)}
            />
          </FormField>
        </Box>
        <Box gap="medium">
          <CheckBoxMergedObjects />
          {hasMultiplexed && <CheckBoxExcludeMultiplexed />}
        </Box>
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
