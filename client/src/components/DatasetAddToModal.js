/* eslint-disable no-nested-ternary */
import React, { useState } from 'react'
import { Anchor, Box, CheckBoxGroup, Grid, Heading, Select } from 'grommet'
import { config } from 'config'
import { useDatasetOptionsContext } from 'hooks/useDatasetOptionsContext'
import { Modal, ModalBody } from 'components/Modal'
import { getReadableOptions } from 'helpers/getReadableOptions'
import { Button } from 'components/Button'
import { CheckBoxBulkRnaSeqDataset } from 'components/CheckBoxBulkRnaSeqDataset'
import { CheckBoxExcludeMultiplexedDataset } from 'components/CheckBoxExcludeMultiplexedDataset'
import { CheckBoxMergedObjectsDataset } from 'components/CheckBoxMergedObjectsDataset'
import { FormField } from 'components/FormField'
import { HelpLink } from 'components/HelpLink'
import { WarningText } from 'components/WarningText'

// Button and Modal to show when adding a project to My Dataset
export const DatasetAddToModal = ({
  label = 'Add to Dataset',
  resource,
  icon = null,
  disabled = false
}) => {
  const {
    format,
    setFormat,
    resourceType,
    formatOptions,
    modalityOptions,
    isSpatialSelected,
    sampleDifferenceForSpatial,
    setSelectedModalities
  } = useDatasetOptionsContext()

  const {
    has_bulk_rna_seq: hasBulkRnaSeq,
    has_multiplexed_data: hasMultiplexed
  } = resource

  const buttonLabel = 'Add to Dataset'
  const modalTitle = `Add ${resourceType} to Dataset`

  const [showing, setShowing] = useState(false)

  const handleClick = () => {
    setShowing(true)
  }

  return (
    <>
      {icon ? (
        <Anchor
          icon={icon}
          onClick={handleClick}
          disabled={disabled}
          label={label}
        />
      ) : (
        <Button
          aria-label={label}
          flex="grow"
          primary
          label={label}
          disabled={disabled}
          onClick={handleClick}
        />
      )}
      <Modal title={modalTitle} showing={showing} setShowing={setShowing}>
        <ModalBody>
          <Grid columns={['auto']} pad={{ bottom: 'medium' }}>
            <Heading level="3" size="small">
              Download Options
            </Heading>
            <Box pad={{ top: 'large' }}>
              <Box gap="medium" pad={{ bottom: 'medium' }} width="680px">
                <FormField
                  label={
                    <HelpLink
                      label="Data Format"
                      link={config.links.what_downloading}
                    />
                  }
                  labelWeight="bold"
                  selectWidth="200px"
                >
                  <Select
                    options={getReadableOptions(formatOptions)}
                    labelKey="label"
                    valueKey={{ key: 'value', reduce: true }}
                    value={format || formatOptions[0]}
                    onChange={({ value }) => setFormat(value)}
                  />
                </FormField>
                <FormField label="Modality" labelWeight="bold">
                  <CheckBoxGroup
                    options={getReadableOptions(modalityOptions)}
                    onChange={(event) => setSelectedModalities(event.value)}
                  />
                </FormField>
                <FormField
                  label="Additional Options"
                  gap="medium"
                  labelWeight="bold"
                >
                  <CheckBoxMergedObjectsDataset
                    label="Merge single-cell samples into 1 object"
                    infoText="Merged objects are not available for projects with multiplexed samples."
                  />
                  {hasBulkRnaSeq && <CheckBoxBulkRnaSeqDataset />}
                  {hasMultiplexed && <CheckBoxExcludeMultiplexedDataset />}
                </FormField>
              </Box>
              <Box align="center" direction="row" gap="xlarge">
                <Button primary aria-label={buttonLabel} label={buttonLabel} />
                {isSpatialSelected && sampleDifferenceForSpatial !== 0 && (
                  <WarningText
                    text={`Selected modalities may not be available for ${sampleDifferenceForSpatial} ${
                      sampleDifferenceForSpatial > 1 ? 'samples' : 'sample'
                    }.`}
                    link="/projects/SCPCP000006"
                    linkLabel=" Inspect"
                    newTab
                  />
                )}
              </Box>
            </Box>
          </Grid>
        </ModalBody>
      </Modal>
    </>
  )
}

export default DatasetAddToModal
