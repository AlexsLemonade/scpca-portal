import React from 'react'
import { Box, Button as GrommetButton, Spinner } from 'grommet'
import { useWaitForAsync } from 'hooks/useWaitForAsync'

export const Button = ({ label, loading, onClick, ...props }) => {
  const [waiting, asyncOnClick] = useWaitForAsync(onClick)
  const disabled = waiting || props.disabled

  const buttonLabel = loading ? (
    <Box align="center">
      <Spinner />
    </Box>
  ) : (
    label
  )

  return (
    <GrommetButton
      // eslint-disable-next-line react/jsx-props-no-spreading
      {...props}
      label={buttonLabel}
      onClick={asyncOnClick}
      disabled={disabled}
      loading={loading}
    />
  )
}

export default Button
