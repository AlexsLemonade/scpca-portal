import React from 'react'
import {config} from 'config'
import { Button } from 'components/Button'
import { HelpLink } from 'components/HelpLink'
import { Grid, Text } from 'grommet'


const saveToClipboard = () => {}


export const CopyLinkButton = ({ ...props}) => {

  return (
    <Grid
      columns={['small', 'small']}
      gap='none'
    >
      <Button
        plain
        label="Copy Download Link"
        onClick={saveToClipboard}
        {...props}
      >
      </Button>
      <HelpLink
        link={config.links.what_copy_link}
      />
    </Grid>
  )
}
