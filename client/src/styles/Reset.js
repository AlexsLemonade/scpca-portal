/* eslint-disable import/prefer-default-export */
import { createGlobalStyle } from 'styled-components'
import styledReset from 'styled-reset'

export const Reset = createGlobalStyle`
  ${styledReset}
  html, body {
    display: flex;
    flex-direction: column;
    position: relative;
  }
`

export default Reset
