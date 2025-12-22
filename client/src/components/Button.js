import React from 'react'
import {
  Button as GrommetButton,
  Spinner as GrommetSpinner,
  Text
} from 'grommet'
import { useWaitForAsync } from 'hooks/useWaitForAsync'
import styled, { css } from 'styled-components'

const ButtonText = styled(Text)`
  ${({ loading }) =>
    css`
      visibility: ${loading ? 'hidden' : 'visible'};
    `}
`

const ButtonSpinner = styled(GrommetSpinner)`
  border-color: white;
  border-width: 3px;
  border-right-color: transparent;
  position: absolute;
  top: 10%;
  left: 40%;
  transform: translate(-10%, -40%);
  ${({ loading }) =>
    css`
      visibility: ${loading ? 'visible' : 'hidden'};
    `}
`

const ButtonLabel = ({ label, loading }) => (
  <>
    <ButtonText loading={loading}>{label}</ButtonText>
    <ButtonSpinner loading={loading} />
  </>
)

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
      label={<ButtonLabel label={label} loading={loading} />}
      onClick={asyncOnClick}
      disabled={disabled}
      loading={loading}
    />
  )
}

export default Button
