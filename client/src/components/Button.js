import React from 'react'
import { Button as GrommetButton } from 'grommet'
import useWaitForAsync from 'hooks/useWaitForAsync'

export const Button = ({ onClick, ...props }) => {
  const [waiting, asyncOnClick] = useWaitForAsync(onClick)
  const disabled = waiting || props.disabled

  return (
    // eslint-disable-next-line react/jsx-props-no-spreading
    <GrommetButton {...props} onClick={asyncOnClick} disabled={disabled} />
  )
}

export default Button
