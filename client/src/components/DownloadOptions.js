import { FormField, Grid, Box, Select } from 'grommet'
import { DownloadOption } from 'components/DownloadOption'
import { useDownloadOptionsContext } from 'hooks/useDownloadOptionsContext'
import getReadableOptions from 'helpers/getReadableOptions'
import { HelpLink } from './HelpLink'
import config from 'config'

export const DownloadOptions = ({ handleSelectFile }) => {

  const {
    selectedModality,
    setSelectedModality,
    modalityOptions,
    selectedFormat,
    setSelectedFormat,
    formatOptions,
    computedFile,
    resource
  } = useDownloadOptionsContext(true) // auto apply selections

  return (
    <Grid columns={['auto']} gap="large" pad={{ bottom: 'medium' }}>
      <Box
        direction="row"
        alignContent="between"
        gap="large"
        pad={{ bottom: 'large' }}
        border={{ side: 'bottom', color: 'border-black', size: 'small' }}
      >
        <FormField label="Modality">
          <Select
            options={getReadableOptions(modalityOptions)}
            labelKey="label"
            valueKey={{ key: "value", reduce: true }}
            value={selectedModality}
            onChange={({ value }) => setSelectedModality(value)}
          />
        </FormField>
        <FormField
          label={
            <HelpLink
              label="Data Format"
              link={config.links.what_downloading}
            />
          }
        >
          <Select
            options={getReadableOptions(formatOptions)}
            labelKey="label"
            valueKey={{ key: "value", reduce: true }}
            value={selectedFormat}
            onChange={({ value }) => setSelectedFormat(value)}
          />
        </FormField>
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
