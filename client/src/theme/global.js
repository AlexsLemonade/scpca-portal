import { normalizeColor } from 'grommet/utils'

export default {
  active: {
    background: 'active-background',
    color: 'active-text'
  },
  borderSize: {
    large: '12px',
    medium: '8px',
    small: '3px',
    xlarge: '16px',
    xsmall: '1px'
  },
  breakpoints: {
    large: {},
    medium: {
      value: '1024px'
    },
    small: {
      borderSize: {
        large: '4px',
        medium: '3px',
        small: '2px',
        xlarge: '8px',
        xsmall: '1px'
      },
      edgeSize: {
        hair: '1px',
        large: '16px',
        medium: '8px',
        none: '0px',
        small: '4px',
        xlarge: '32px',
        xsmall: '2px',
        xxsmall: '2px'
      },
      size: {
        full: '100%',
        large: '256px',
        medium: '128px',
        small: '64px',
        xlarge: '512px',
        xsmall: '32px',
        xxsmall: '16px'
      },
      value: 512
    }
  },
  colors: {
    gradient: 'linear-gradient(180deg, #FDFDFD 0%, #EDF7FD 100%)',
    'gradient-reverse': 'linear-gradient(0deg, #FDFDFD 0%, #EDF7FD 100%)',
    'alexs-deep-blue': '#003595',
    'alexs-deep-blue-tint-20': '#3E58AA',
    'alexs-deep-blue-tint-40': '#737EBF',
    'alexs-deep-blue-tint-70': '#B9BCDF',
    'alexs-light-blue': '#145ECC',
    'alexs-light-blue-tint-20': '#437ED6',
    'alexs-light-blue-tint-40': '#729EE0',
    'alexs-light-blue-tint-60': '#B9CFF0',
    'alexs-lemonade': '#FFDD00',
    'alexs-lemonade-tint-20': '#FFE303',
    'alexs-lemonade-tint-40': '#FFE964',
    'alexs-lemonade-tint-60': '#FFF09A',
    'alexs-lemonade-tint-75': '#FFF5C0',
    'powder-blue': '#C9ECFA',
    dawn: '#EDF7FD',
    'soda-orange': '#E55517',
    'soda-orange-tint-20': '#ec7643',
    'soda-orange-tint-40': '#F09872',
    'soda-orange-tint-60': '#F5BAA1',
    'soda-orange-tint-80': '#FADCD0',
    'soda-orange-tint-90': '#FCEDE7',
    'soda-orange-shade-20': '#B74412',
    'soda-orange-shade-40': '#89320D',
    'soda-orange-shade-60': '#5B2209',
    'savana-green': '#98BF61',
    'savana-green-tint-40': '#C1D8A0',
    'savana-green-tint-60': '#D5E5BF',
    'savana-green-tint-80': '#EAF2DF',
    'savana-green-shade-20': '#7BA342',
    'savana-green-shade-40': '#5C7A31',
    'savana-green-shade-60': '#3D5121',
    'savana-green-shade-80': '#1E2810',
    black: '#000000',
    'black-tint-20': '#333333',
    'black-tint-30': '#4A4A4A',
    'black-tint-40': '#666666',
    'black-tint-60': '#999999',
    'black-tint-80': '#CCCCCC',
    'black-tint-90': '#E5E5E5',
    'black-tint-95': '#F2F2F2',
    white: '#FDFDFD',
    info: '#003595', // alexs-deep-blue
    success: '#41A36D',
    'success-shade-20': '#348257',
    error: '#DB3B28',
    'error-shade-20': '#A72A1B',
    warning: '#FFDD00', // alexs-lemonade
    'active-background': 'brand',
    'active-text': 'text-strong',
    'background-highlight': '#F2F2F2',
    background: {
      dark: '#111111',
      light: 'white'
    },
    'background-back': {
      dark: '#111111',
      light: 'white'
    },
    'background-contrast': {
      dark: '#FFFFFF',
      light: 'white'
    },
    'background-front': {
      dark: '#222222',
      light: 'white'
    },
    border: {
      dark: '#444444',
      light: '#cccccc'
    },
    brand: {
      dark: 'alexs-deep-blue',
      light: 'alexs-deep-blue'
    },
    control: 'brand',
    'graph-0': 'brand',
    'graph-1': 'status-warning',
    'selected-background': 'brand',
    'selected-text': 'text',
    'status-critical': '#FF4040',
    'status-disabled': '#CCCCCC',
    'status-ok': '#00C781',
    'status-unknown': '#CCCCCC',
    'status-warning': '#FFAA15',
    text: {
      dark: '#FDFDFD',
      light: '#000000'
    },
    'text-strong': {
      dark: '#FFFFFF',
      light: '#000000'
    },
    'text-weak': {
      dark: '#CCCCCC',
      light: '#999999'
    },
    'text-xweak': {
      dark: '#999999',
      light: '#666666'
    },
    focus: 'brand',
    'border-black': '#F2F2F2',
    'border-brand': '#BAEFFE'
  },
  control: {
    border: {
      radius: '4px'
    }
  },
  drop: {
    border: {
      radius: '4px'
    },
    extend: (props) => `
      border: 1px solid ${normalizeColor('black-tint-60', props.theme)};
      margin-top: 4px;
    `,
    active: {
      background: 'red'
    }
  },
  edgeSize: {
    hair: '1px',
    large: '32px',
    medium: '16px',
    none: '0px',
    responsiveBreakpoint: 'small',
    small: '8px',
    xlarge: '48px',
    xxlarge: '64px',
    gutter: '40px',
    xsmall: '4px',
    xxsmall: '2px'
  },
  elevation: {
    light: {
      medium: '0 2px 18px 1px rgba(0, 0, 0, 0.1)'
    }
  },
  font: {
    family: 'Source Sans Pro',
    height: '24px',
    maxWidth: '192px',
    size: '16px'
  },
  hover: {
    background: 'active-background',
    color: 'active-text'
  },
  input: {
    font: {
      height: '28px'
    },
    padding: '6px',
    weight: 400
  },
  selected: {
    background: 'selected-background',
    color: 'selected-text'
  },
  size: {
    full: '100%',
    large: `${8 * 91}px`,
    medium: `${8 * 65}px`,
    small: '258px',
    xlarge: `${8 * 130}px`,
    xsmall: '64px',
    xxlarge: `${8 * 156}px`,
    xxsmall: '32px'
  },
  spacing: '16px'
}
