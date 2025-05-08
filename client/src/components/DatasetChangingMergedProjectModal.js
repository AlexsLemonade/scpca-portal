import React, { useState } from 'react'
import { Box, Text } from 'grommet'
import { config } from 'config'
import { Button } from 'components/Button'
import { Modal, ModalBody } from 'components/Modal'
import { WarningText } from 'components/WarningText'
import { InfoText } from 'components/InfoText'
import { Link } from 'components/Link'

export const DatasetChangingMergedProjectModal = ({
  label = 'Save Changes',
  title = 'Changing a Merged Project',
  disabled = false
}) => {
  const [showing, setShowing] = useState(false)

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
      <Modal showing={showing} setShowing={setShowing}>
        <Box
          border={{
            side: 'bottom',
            color: 'border-black',
            size: 'small'
          }}
          gridArea="title"
          width="full"
          height={{ min: 'min-content' }}
          pad={{ left: 'medium' }}
          margin={{ bottom: '24px' }}
        >
          <WarningText
            lineBreak={false}
            iconMargin="0"
            iconSize="24px"
            margin={false}
          >
            <Text size="xlarge">{title}</Text>
          </WarningText>
        </Box>
        <ModalBody>
          <Text margin={{ left: 'xsmall' }}>
            You have selected to merge all single-cell samples into one object.
          </Text>
          <Text margin={{ left: 'xsmall', top: 'medium' }}>
            We cannot merge samples into one object if you remove single-cell
            samples from the project.
          </Text>
          <Box margin={{ top: 'medium' }}>
            <InfoText>
              <Link
                href={config.links.why_changing_merged_project}
                label="Learn more"
              />
            </InfoText>
          </Box>
          <Box
            align="center"
            direction="row"
            gap="xlarge"
            justify="end"
            margin={{ top: 'large' }}
          >
            <Button
              aria-label="Cancel"
              label="Cancel"
              onClick={() => setShowing(false)}
            />
            <Button primary aria-label="Continue" label="Continue" />
          </Box>
        </ModalBody>
      </Modal>
    </>
  )
}
