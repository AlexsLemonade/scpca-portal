const defaultBorder = { radius: '4px', width: '1px' }

export default {
  color: 'brand',
  default: {
    color: 'brand',
    border: { color: 'brand', ...defaultBorder },
    padding: {
      horizontal: '24px',
      vertical: '7px' // 8px - 1px for border
    }
  },
  primary: {
    background: { color: 'brand' },
    border: { color: 'brand', ...defaultBorder },
    color: 'white',
    padding: {
      horizontal: '24px',
      vertical: '7px' // 8px - 1px for border
    }
  },
  secondary: {
    border: { color: 'brand', ...defaultBorder },
    color: 'text',
    padding: {
      horizontal: '24px',
      vertical: '7px' // 8px - 1px for border
    }
  },
  active: {
    background: { color: 'brand-contrast' },
    color: 'text',
    secondary: {
      background: 'none',
      border: { color: 'brand-contrast', ...defaultBorder }
    }
  },
  disabled: {
    opacity: 1,
    shadow: undefined,
    color: 'text-weak',
    background: 'black-tint-90',
    border: { color: 'black-tint-90', ...defaultBorder },
    primary: { color: 'black-tint-40', background: 'black-tint-70' }
  },
  hover: {
    background: { color: 'brand' },
    disabled: undefined
  },
  extend: () => `
    white-space: nowrap;
    &:active:not([disabled]) {
      box-shadow: 0 3px 4px 0 rgba(0,0,0,0.5);
    }
  `
}
