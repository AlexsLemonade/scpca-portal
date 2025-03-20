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
  disabled = false
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
        disabled={disabled}
        onClick={handleClick}
      />
      <Modal title={title} showing={showing} setShowing={setShowing}>
        <ModalBody>
          <WarningText
            lineBreak={false}
            iconMargin="0"
            iconSize="24px"
            margin={false}
          >
            <Text size="21px" margin={{ left: 'xsmall' }}>
              There are {totalSamples} samples in My Dataset
            </Text>
          </WarningText>
          <FormField>
            <RadioButtonGroup
              name="action"
              options={radioOptions}
              value={action}
              onChange={({ target: { value } }) => setAction(value)}
            />
          </FormField>
          <Box margin={{ top: 'medium' }}>
            <InfoText iconSize="24px">
              <Text margin={{ left: 'small' }}>
                Some download options may have changed. Please review the
                dataset before you download.{' '}
                <Link
                  href={config.links.what_review_dataset}
                  label="Learn more"
                />
              </Text>
            </InfoText>
          </Box>
          <Box
            align="center"
            direction={responsive('column', 'row')}
            gap="xlarge"
            justify="end"
            margin={{ top: 'large' }}
          >
            <Button primary aria-label={label} label={label} />
          </Box>
        </ModalBody>
      </Modal>
    </>
  )
}
