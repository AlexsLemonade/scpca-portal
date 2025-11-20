import React from 'react'
import { Heading, Grid, Box, Select } from 'grommet'
import { config } from 'config'
import { useResponsive } from 'hooks/useResponsive'
import { useCCDLDatasetDownloadModalContext } from 'hooks/useCCDLDatasetDownloadModalContext'
import { CCDLDatasetCheckBoxMergedObjects } from 'components/CCDLDatasetCheckBoxMergedObjects'
import { CCDLDatasetCheckBoxExcludeMultiplexed } from 'components/CCDLDatasetCheckBoxExcludeMultiplexed'
import { CCDLDatasetDownloadOption } from 'components/CCDLDatasetDownloadOption'
import { FormField } from 'components/FormField'
import { HelpLink } from 'components/HelpLink'
import { getReadable, getStorable } from 'helpers/getReadable'

export const CCDLDatasetDownloadOptions = () => {
  const {
    modality,
    setModality,
    format,
    setFormat,
    selectedDataset,
    isMultiplexedAvailable,
    modalityOptions,
    formatOptions
  } = useCCDLDatasetDownloadModalContext()

  const { responsive } = useResponsive()
  const showMultiplexedOption = isMultiplexedAvailable

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
          <FormField
            label="Modality"
            direction={responsive('column', 'row')}
            align={responsive('start', 'center')}
            fieldWidth="116px"
          >
            <Select
              options={modalityOptions}
              value={getReadable(modality)}
              onChange={({ value }) => setModality(getStorable(value.label))}
            />
          </FormField>
          <FormField
            label={
              <HelpLink
                label="Data Format"
                link={config.links.what_downloading}
              />
            }
            direction={responsive('column', 'row')}
            align={responsive('start', 'center')}
            fieldWidth="200px"
          >
            <Select
              options={formatOptions}
              value={getReadable(format)}
              onChange={({ value }) => setFormat(getStorable(value.label))}
            />
          </FormField>
        </Box>
        <Box gap="medium">
          <CCDLDatasetCheckBoxMergedObjects />
          {showMultiplexedOption && <CCDLDatasetCheckBoxExcludeMultiplexed />}
        </Box>
      </Box>
      <Box>
        {selectedDataset.computed_file && <CCDLDatasetDownloadOption />}
      </Box>
    </Grid>
  )
}

export default CCDLDatasetDownloadOptions
