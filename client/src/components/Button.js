import React from 'react'
import { Button as GrommetButton, Spinner } from 'grommet'
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
  awaiting = false,
  onClick = () => {},
  ...props
}) => {
  const [waiting, asyncOnClick] = useWaitForAsync(onClick)
  const disabled = waiting || awaiting || props.disabled

  return (
    <GrommetButton
      // eslint-disable-next-line react/jsx-props-no-spreading
      {...props}
      icon={awaiting ? <LoadingSpinner /> : undefined}
      label={awaiting ? undefined : label}
      onClick={asyncOnClick}
      disabled={disabled}
      awaiting={awaiting}
    />
  )
}

export default Button
