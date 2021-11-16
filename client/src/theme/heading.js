import { applyWhen } from 'helpers/applyWhen'

export default {
  font: {
    family: 'Source Sans Pro',
    weight: 'bold'
  },
  extend: (props) =>
    applyWhen(props.serif, `font-family: 'Zilla Slab'; font-weight: 500`),
  level: {
    1: {
      large: {
        height: '59px',
        maxWidth: null,
        size: '55px'
      },
      medium: {
        height: 1.5,
        maxWidth: null,
        size: '67px'
      },
      small: {
        height: '27px',
        maxWidth: null,
        size: '23px'
      },
      xlarge: {
        height: '80px',
        maxWidth: null,
        size: '76px'
      }
    },
    2: {
      large: {
        height: '40px',
        maxWidth: null,
        size: '36px'
      },
      medium: {
        height: 1.5,
        maxWidth: null,
        size: '50px'
      },
      small: {
        height: '24px',
        maxWidth: null,
        size: '20px'
      },
      xlarge: {
        height: '48px',
        maxWidth: null,
        size: '44px'
      }
    },
    3: {
      large: {
        height: '32px',
        maxWidth: null,
        size: '28px'
      },
      medium: {
        height: 1.5,
        maxWidth: null,
        size: '38px'
      },
      small: {
        height: '21px',
        maxWidth: null,
        size: '17px'
      },
      xlarge: {
        height: '37px',
        maxWidth: null,
        size: '33px'
      }
    },
    4: {
      large: {
        height: '24px',
        maxWidth: null,
        size: '20px'
      },
      medium: {
        height: 1.5,
        maxWidth: null,
        size: '28px'
      },
      small: {
        height: '19px',
        maxWidth: null,
        size: '15px'
      },
      xlarge: {
        height: '27px',
        maxWidth: null,
        size: '23px'
      }
    },
    5: {
      large: {
        height: '15px',
        maxWidth: null,
        size: '11px'
      },
      medium: {
        height: 1.524,
        maxWidth: null,
        size: '21px'
      },
      small: {
        height: '15px',
        maxWidth: null,
        size: '11px'
      },
      xlarge: {
        height: '15px',
        maxWidth: null,
        size: '11px'
      }
    },
    6: {
      large: {
        height: '13px',
        maxWidth: null,
        size: '9px'
      },
      medium: {
        height: '13px',
        maxWidth: null,
        size: '9px'
      },
      small: {
        height: '13px',
        maxWidth: null,
        size: '9px'
      },
      xlarge: {
        height: '13px',
        maxWidth: null,
        size: '9px'
      }
    }
  }
}
