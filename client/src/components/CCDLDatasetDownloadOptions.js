import React from 'react'
import { Heading, Grid, Box, Select } from 'grommet'
import { config } from 'config'
import { useResponsive } from 'hooks/useResponsive'
import { useCCDLDatasetDownload } from 'hooks/useCCDLDatasetDownload'
import { CCDLDatasetCheckBoxMergedObjects } from 'components/CCDLDatasetCheckBoxMergedObjects'
import { CCDLDatasetCheckBoxExcludeMultiplexed } from 'components/CCDLDatasetCheckBoxExcludeMultiplexed'
import { CCDLDatasetDownloadOption } from 'components/CCDLDatasetDownloadOption'
import { FormField } from 'components/FormField'
import { HelpLink } from 'components/HelpLink'
import { getReadableOptions } from 'helpers/getReadableOptions'
import { getReadable, getStorable } from 'helpers/getReadable'

export const CCDLDatasetDownloadOptions = ({ handleSelectedDataset }) => {
  const {
    modalityOptions,
    formatOptions,
    modality,
    setModality,
    format,
    setFormat,
    includesMerged,
    setIncludesMerged,
    isMergedObjectsAvailable,
    excludeMultiplexed,
    setExcludeMultiplexed,
    isExcludeMultiplexedAvailable,
    showingDataset
  } = useCCDLDatasetDownload()

  const { responsive } = useResponsive()
  const showMultiplexedOption = isExcludeMultiplexedAvailable

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
              options={getReadableOptions(modalityOptions)}
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
              options={getReadableOptions(formatOptions)}
              value={getReadable(format)}
              onChange={({ value }) => setFormat(getStorable(value.label))}
            />
          </FormField>
        </Box>
        <Box gap="medium">
          <CCDLDatasetCheckBoxMergedObjects
            includesMerged={includesMerged}
            setIncludesMerged={setIncludesMerged}
            isMergedObjectsAvailable={isMergedObjectsAvailable}
          />
          {showMultiplexedOption && (
            <CCDLDatasetCheckBoxExcludeMultiplexed
              excludeMultiplexed={excludeMultiplexed}
              setExcludeMultiplexed={setExcludeMultiplexed}
              isExcludeMultiplexedAvailable={isExcludeMultiplexedAvailable}
            />
          )}
        </Box>
      </Box>
      <Box>
        {showingDataset.computed_file && (
          <CCDLDatasetDownloadOption
            dataset={showingDataset}
            handleSelectedDataset={handleSelectedDataset}
          />
        )}
      </Box>
    </Grid>
  )
}

export default CCDLDatasetDownloadOptions
