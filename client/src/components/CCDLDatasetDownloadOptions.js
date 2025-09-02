import React, { useState } from 'react'
import { Heading, Grid, Box, Select } from 'grommet'
import { config } from 'config'
import { useResponsive } from 'hooks/useResponsive'
import { CheckBoxMergedObjects } from 'components/CheckBoxMergedObjects'
import { CheckBoxExcludeMultiplexed } from 'components/CheckBoxExcludeMultiplexed'
import { CCDLDatasetDownloadOption } from 'components/CCDLDatasetDownloadOption'
import { FormField } from 'components/FormField'
import { HelpLink } from 'components/HelpLink'

export const CCDLDatasetDownloadOptions = ({ datasets, handleSelectFile }) => {
  const hasMultiplexed = false
  const { responsive } = useResponsive()
  const [selectedDataset, setSelectedDataset] = useState([])

  // TODO: apply dataset selection logic through a hook or context
  setSelectedDataset(datasets[0])

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
            <Select options={[]} value="" onChange={() => {}} />
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
            <Select options={[]} value="" onChange={() => {}} />
          </FormField>
        </Box>
        <Box gap="medium">
          <CheckBoxMergedObjects />
          {hasMultiplexed && <CheckBoxExcludeMultiplexed />}
        </Box>
      </Box>
      <Box>
        {selectedDataset.computed_file && (
          <CCDLDatasetDownloadOption
            dataset={selectedDataset}
            handleSelectFile={handleSelectFile}
          />
        )}
      </Box>
    </Grid>
  )
}

export default CCDLDatasetDownloadOptions
