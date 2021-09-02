import { normalizeColor } from 'grommet/utils'
import applyAll from 'helpers/applyAll'
import applyWhen from 'helpers/applyWhen'

export default {
  border: {
    radius: '4px',
    width: '1px'
  },
  padding: {
    horizontal: '24px',
    vertical: '7px' // 8px - 1px for border
  },
  size: {
    medium: {
      border: {
        radius: '4px'
      },
      padding: {
        horizontal: '24px',
        vertical: '7px' // 8px - 1px for border
      }
    }
  },
  disabled: {
    opacity: 1
  },
  extend: ({ theme }, ...props) =>
    applyAll(
      applyWhen(
        !props.plain && !props.role,
        `
        ${applyWhen(
          !props.primary && !props.disabled,
          `
            color: ${normalizeColor('brand', theme)};
            &:hover, &:active {
              box-shadow: none;
              background-color: ${normalizeColor('alexs-deep-blue', theme)};
              color: ${normalizeColor('white', theme)};
            }
            &:active {
              box-shadow: 0 3px 4px 0 rgba(0,0,0,0.5);
            }
          `
        )}
         ${applyWhen(
           !props.primary && props.disabled,
           `
             color: ${normalizeColor('black-tint-60', theme)};
             background-color: ${normalizeColor('white', theme)};
             border-color: ${normalizeColor('black-tint-60', theme)};
           `
         )}
         ${applyWhen(
           props.primary && !props.disabled,
           `
           color: ${normalizeColor('white', theme)};
           &:hover, &:active {
             box-shadow: none;
             background-color: ${normalizeColor(
               'alexs-deep-blue-tint-20',
               theme
             )};
           }
           &:active {
             box-shadow: 0 3px 4px 0 rgba(0,0,0,0.5);
           }
         `
         )}
         ${applyWhen(
           props.primary && props.disabled,
           `
             color: ${normalizeColor('white', theme)};
             background-color: ${normalizeColor('black-tint-60', theme)};
             border-color: ${normalizeColor('black-tint-60', theme)};
           `
         )}
         `
      ),
      applyWhen(
        props.plain && props.role === 'menuitem',
        `
          background-color: transparent;
          > div {
            padding: 4px 8px;
          }
          ${applyWhen(
            !props.selected,
            `
               &:hover {
                 background-color: ${normalizeColor('black-tint-90', theme)};
                 span {
                   color: ${normalizeColor('brand', theme)};
                 }
               }
             `
          )}
          ${applyWhen(
            props.selected || props.active,
            `
              background-color: ${normalizeColor('brand', theme)};
              span {
                color: ${normalizeColor('white', theme)};
              }
            `
          )}
        `
      ),
      applyWhen(
        props.plain &&
          !props.role &&
          !props.colorValue &&
          !(props.hoverIndicator === 'background'), // exclude suggestions
        `
          color: ${normalizeColor('brand', theme)};
          input {
            color: ${normalizeColor('black', theme)};
          }
        `
      ),
      applyWhen(
        props.plain && !props.role && props.disabled,
        `
          color: ${normalizeColor('black-tint-60', theme)};
         `
      ),
      applyWhen(
        props.login,
        `
          color: ${normalizeColor('black', theme)};
          border: none;
          background-color: ${normalizeColor('white', theme)};
          input {
            color: ${normalizeColor('black', theme)};
          }
          &:hover {
            background-color: ${normalizeColor('black-tint-90', theme)};
            color: ${normalizeColor('black', theme)};
          }
     `
      ),
      applyWhen(
        props.critical && !props.disabled,
        `
          color: ${normalizeColor('error', theme)};
          border-color: ${normalizeColor('error', theme)};
          background-color: ${normalizeColor('white', theme)};
          input {
            color: ${normalizeColor('error', theme)};
          }
          &:hover {
            background-color: ${normalizeColor('error', theme)};
            color: ${normalizeColor('white', theme)};
          }
        `
      ),
      applyWhen(
        props.success && !props.disabled,
        `
          color: ${normalizeColor('success', theme)};
          border-color: ${normalizeColor('success', theme)};
          background-color: ${normalizeColor('white', theme)};
          input {
            color: ${normalizeColor('success', theme)};
          }
          &:hover {
            background-color: ${normalizeColor('success', theme)};
            color: ${normalizeColor('white', theme)};
          }
        `
      ),
      applyWhen(props.plain && props.underline, 'text-decoration: underline;'),
      applyWhen(props.plain && props.bold, 'font-weight: bold;')
    )
}
