import React, { useState } from 'react'
import { Box, Grid, RadioButtonGroup, Text } from 'grommet'
import { config } from 'config'
import { useResponsive } from 'hooks/useResponsive'
import { Button } from 'components/Button'
import { Modal, ModalBody } from 'components/Modal'
import { WarningText } from 'components/WarningText'
import { InfoText } from 'components/InfoText'
import { Link } from 'components/Link'
import { FormField } from 'components/FormField'

export const DatasetMoveSamplesModal = ({
  label = 'Move Samples',
  title = 'Move Samples to My Dataset',
  modalDisabled = false,
  appendDisabled = false
}) => {
  const [showing, setShowing] = useState(false)
  const radioOptions = [
    { label: 'Append samples to My Dataset', value: 'append' },
    { label: 'Replace samples in My Dataset', value: 'replace' }
  ]
  const [action, setAction] = useState(radioOptions[0].value)

  const { responsive } = useResponsive()
  const totalSamples = 34

  const handleClick = () => {
    setShowing(true)
  }

  return (
    <>
      <Button
        aria-label={label}
        flex="grow"
        primary
        label={label}
        disabled={modalDisabled}
        onClick={handleClick}
      />
      <Modal title={title} showing={showing} setShowing={setShowing}>
        <ModalBody>
          <Grid
            columns={['auto']}
            margin={{ bottom: '0' }}
            pad={{ bottom: '0' }}
          >
            <Box>
              <WarningText
                lineBreak={false}
                text={`There are ${totalSamples} samples in My Dataset`}
                iconMargin="0"
              />
            </Box>
            <FormField>
              <RadioButtonGroup
                name="action"
                options={radioOptions}
                value={action}
                onChange={({ target: { value } }) => setAction(value)}
              />
            </FormField>
            {!appendDisabled && (
              <InfoText>
                <Text>
                  Some download options may have changed. Please review the
                  dataset before you download.{' '}
                  <Link
                    href={config.links.what_review_dataset}
                    label="Learn more"
                  />
                </Text>
              </InfoText>
            )}
            <Box
              align="center"
              direction={responsive('column', 'row')}
              gap="xlarge"
              justify="end"
            >
              <Button primary aria-label={label} label={label} />
            </Box>
          </Grid>
        </ModalBody>
      </Modal>
    </>
  )
}
