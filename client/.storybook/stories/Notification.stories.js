import React from "react"
import { useNotification } from 'hooks/useNotification'
import { Box } from 'grommet'
import { Button } from 'components/Button'
import { Notification } from 'components/Notification'

export default {
    title: 'Components/Notification'
}

const Success = ({ id='notification-success' }) => {
    const { showNotification } = useNotification()

    return (
        <>
           <Notification id={id}>
                This is a success notification!
           </Notification>
           <Box width='250px' margin={{top: 'large'}}>
                <Button
                    label="Success Notification"
                    onClick={()=> showNotification(id, 'success')}
                />
           </Box>
        </>
    )
}

const Error = ({ id='notification-error' }) => {
    const { showNotification } = useNotification()

    return (
        <>
           <Notification id={id}>
              This is an error notification!
           </Notification>
           <Box width='250px' margin={{top: 'large'}}>
                <Button
                    label="Error Notification"
                    onClick={()=> showNotification(id, 'error')}
                />
           </Box>
        </>
    )
}


const MoveSamplesSuccess= ({ id='move-samples-success' }) => {
    const { showNotification } = useNotification()
    const totalSamples = 20
    const content = `Move ${totalSamples} Samples to My Dataset`

    return (
        <>
           <Notification id={id} >{content}</Notification>
           <Box width='250px' margin={{top: 'large'}}>
                <Button
                   label="Move Samples Notification"
                   onClick={()=> showNotification(id, 'success')}
                />
            </Box>
        </>
    )
}


export const Default = () => {
    return (
      <Box
        align="center"
        gap="large"
        justify="center"
        margin={{ top: 'large' }}
        width='fill'>
          <Success />
          <Error />
          <MoveSamplesSuccess />

      </Box>
    )
  }
