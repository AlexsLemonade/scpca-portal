import applyAll from 'helpers/applyAll'
import applyWhen from 'helpers/applyWhen'

export default {
  extend: (props) =>
    applyAll(
      applyWhen(props.italic, 'font-style: italic'),
      applyWhen(
        props.serif,
        `
          font-family: 'Zilla Slab';
          font-weight: 500;
        `
      )
    ),
  large: {
    height: '32px',
    maxWidth: '235px',
    size: '21px'
  },
  medium: {
    height: '24px',
    maxWidth: '192px',
    size: '16px'
  },
  small: {
    height: '18px',
    maxWidth: '171px',
    size: '12px'
  },
  xlarge: {
    height: '42px',
    maxWidth: '277px',
    size: '28px'
  },
  xsmall: {
    height: '13px',
    maxWidth: '149px',
    size: '9px'
  },
  xxlarge: {
    height: '53px',
    maxWidth: '660px',
    size: '38px'
  }
}
