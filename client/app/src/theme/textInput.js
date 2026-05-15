import { applyWhen } from 'helpers/applyWhen'

export default {
  extend: (props) => applyWhen(props.focus, 'box-shadow: none;')
}
