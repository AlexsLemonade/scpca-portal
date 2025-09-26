import React from 'react'
import { Heading, Grid, Box, Select } from 'grommet'
import { config } from 'config'
import { useResponsive } from 'hooks/useResponsive'
import { useCCDLDatasetDownloadOptions } from 'hooks/useCCDLDatasetDownloadOptions'
import { CheckBoxMergedObjects } from 'components/CheckBoxMergedObjects'
import { CheckBoxExcludeMultiplexed } from 'components/CheckBoxExcludeMultiplexed'
import { CCDLDatasetDownloadOption } from 'components/CCDLDatasetDownloadOption'
import { FormField } from 'components/FormField'
import { HelpLink } from 'components/HelpLink'

export const CCDLDatasetDownloadOptions = ({
  datasets,
  handleSelectedDataset
}) => {
  const { responsive } = useResponsive()
  const showMultiplexedOption = false

  const {
    modalityOptions,
    formatOptions,
    modality,
    setModality,
    format,
    setFormat,
    showingDataset
  } = useCCDLDatasetDownloadOptions(datasets)

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
            direction={responsive('column', 'row')}
            align={responsive('start', 'center')}
            fieldWidth="200px"
          >
            <Select
              options={formatOptions}
              value={format}
              onChange={({ value }) => setFormat(value)}
            />
          </FormField>
        </Box>
        <Box gap="medium">
          <CheckBoxMergedObjects />
          {showMultiplexedOption && <CheckBoxExcludeMultiplexed />}
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
