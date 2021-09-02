import applyWhen from 'helpers/applyWhen'

export default {
  fontWeight: 400,
  extend: (props) => applyWhen(props.bold, 'font-weight: 600')
}
