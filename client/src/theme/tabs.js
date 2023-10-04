export default {
  background: undefined,
  header: {
    border: {
      side: 'bottom',
      color: 'border',
      size: '2px'
    },
    extend: ({ theme }) => `
      justify-content: start;
      padding: 0;

      button {
        margin-right: 24px;
        transform: translate(0, 2px);
        
        div {
          padding: 0 0 8px;
        }

        span {
          color: ${theme.global.colors.black};
          font-size: 21px;
          line-height: 32px;
        }
      }

      button:hover {
        background-color: transparent;
      }

      > button[aria-expanded="true"] {
        border-bottom: 2px solid ${theme.global.colors.brand.light};

        span {
          color: ${theme.global.colors.brand.light};
        }
      }
    `
  }
}
