import applyAll from 'helpers/applyAll'
import applyWhen from 'helpers/applyWhen'

export default {
  border: {
    color: 'black-tint-60',
    error: {
      size: '12px',
      color: {
        dark: 'white',
        light: 'status-critical'
      }
    },
    position: 'inner',
    side: 'all',
    size: 'xsmall',
    style: 'solid'
  },
  content: {
    pad: 'medium'
  },
  disabled: {
    background: {
      color: 'status-disabled',
      opacity: 'medium'
    }
  },
  error: {
    color: 'status-critical',
    margin: {
      horizontal: 'none',
      vertical: 'xsmall'
    }
  },
  help: {
    color: 'black-tint-40',
    margin: {
      start: 'none',
      bottom: 'xsmall'
    }
  },
  info: {
    color: 'text-xweak',
    margin: {
      horizontal: 'none',
      vertical: 'xsmall'
    }
  },
  label: {
    margin: {
      horizontal: 'none',
      bottom: '12px' // plus 4 = 16px
    },
    size: 'medium'
  },
  margin: {
    vertical: 'medium'
  },
  round: '4px',
  extend: (props) =>
    applyAll(
      `
       // FormField help
       // Same styles as components/InputHelperText.js
       // Which is used for MarkDown type helper text
       label + span {
         font-style: italic;
         font-size: 12px;
         line-height: 18px;
       }
         button, input, textarea {
         border: none;
       }
       `,
      applyWhen(
        props.checkbox,
        `
      > div {
        border: none;
        > div {
          padding: 0;
        }
      }
      `
      ),
      applyWhen(
        props.borderless,
        `
        > div {
          border: none;
        }
        `
      )
    )
}
