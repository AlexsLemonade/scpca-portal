import React from 'react'
import { Box, Button as GrommetButton, Spinner, Text } from 'grommet'
import { useWaitForAsync } from 'hooks/useWaitForAsync'

const LoadingSpinner = () => {
  return (
    <Spinner
      border={[
        { side: 'all', color: 'white', size: 'small' },
        { side: 'right', color: 'transparent', size: 'small' }
      ]}
    />
  )
}

export const Button = ({
  label,
  loading = false,
  onClick = () => {},
  ...props
}) => {
  const [waiting, asyncOnClick] = useWaitForAsync(onClick)
  const disabled = waiting || loading || props.disabled

  return (
    <GrommetButton
      // eslint-disable-next-line react/jsx-props-no-spreading
      {...props}
      label={
        <Box style={{ position: 'relative' }}>
          <Text color={loading ? 'transparent' : 'inherit'}>{label}</Text>
          {loading && (
            <Box
              style={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)'
              }}
            >
              <LoadingSpinner />
            </Box>
          )}
        </Box>
      }
      onClick={asyncOnClick}
      disabled={disabled}
      loading={loading}
    />
  )
}

export default Button
