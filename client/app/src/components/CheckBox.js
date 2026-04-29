import { CheckBox as GrommetCheckBox } from 'grommet'
import styled, { css } from 'styled-components'

export const CheckBox = styled(GrommetCheckBox)`
  + div {
    width: 24px;
    height: 24px;
  }
  ${({ theme }) => css`
    &:not(:checked) {
      + div {
        background: ${theme.global.colors.white};
      }
    }
  `}
`

export default CheckBox
