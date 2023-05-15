import { PageLoader } from 'components/PageLoader'
import styled from 'styled-components'


export const ProgressBar = styled(PageLoader)`
  position: absolute;
  top: 100%;
  width: 100%;
  z-index: -1;
  transform: translate(0, -100%);
  height: 12px;
`

export default ProgressBar