export default {
  background: undefined,
  header: {
    border: {
      side: 'bottom',
      color: 'border',
      size: 'xsmall'
    },
    extend: ({ theme }) => `
      justify-content: start;
      padding: 0 16px;

      button {
        transform: translate(0, 1px)
      }

      button:hover {
        background-color: transparent;
      }

      > button[aria-expanded="true"] {
        font-weight: 700;
        border-left: 1px solid ${theme.global.colors.border.light};
        border-top: 1px solid ${theme.global.colors.border.light};
        border-right: 1px solid ${theme.global.colors.border.light};
        border-bottom: 1px solid ${theme.global.colors.background.light};
      }
    `
  }
}
