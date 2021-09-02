import React from 'react'
import { Blank } from 'grommet-icons'
import { normalizeColor } from 'grommet/utils'
import applyAll from 'helpers/applyAll'
import applyWhen from 'helpers/applyWhen'

const DownArrow = (props) => (
  // eslint-disable-next-line react/jsx-props-no-spreading
  <Blank {...props}>
    <polygon points="4,8 20,8 12,16" stroke="#000" fill="#000" />
  </Blank>
)

export default {
  icons: {
    margin: 'none',
    color: 'black-tint-40',
    down: DownArrow
  },
  control: {
    border: {
      radius: '4px'
    },
    extend: (props) =>
      applyAll(
        `
          border-radius: 4px;
          border-color: ${normalizeColor('black-tint-60', props.theme)};
        `,
        applyWhen(
          props.open,
          `background-color: ${normalizeColor('black-tint-80', props.theme)};`
        ),
        applyWhen(
          !props.disabled,
          `
            background-color: ${normalizeColor('white', props.theme)};
          `
        ),
        applyWhen(
          props.disabled,
          `
            border-color: ${normalizeColor('black-tint-60', props.theme)};
           background-color: ${normalizeColor('black-tint-95', props.theme)};
         `
        )
      )
  },
  options: {
    text: {
      color: 'black'
    }
  }
}
