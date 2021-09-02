import applyWhen from 'helpers/applyWhen'

export default {
  color: 'brand',
  check: {
    radius: '4px'
  },
  size: '16px',
  toggle: {
    radius: '16px',
    size: '32px'
  },
  border: {
    width: '1px',
    color: {
      dark: 'black-tint-80',
      light: 'black-tint-80'
    }
  },
  hover: {
    border: {
      color: {
        dark: 'black-tint-60',
        light: 'black-tint-60'
      }
    }
  },
  margin: {
    vertical: 'small'
  },
  extend: (props) =>
    applyWhen(
      !props.reverse,
      `
        align-items: start;
        margin: 0 8px;
        div:first-child {
          margin-top: 4px;
        }
      `
    )
}
