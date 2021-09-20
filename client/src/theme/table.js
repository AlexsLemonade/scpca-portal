export default {
  header: {
    border: undefined,
    fill: 'horizontal',
    pad: { horizontal: 'medium', vertical: 'small' },
    verticalAlign: 'bottom',
    extend: `
      font-weight: bold;
      box-shadow: 0.5px 0 0 0 #999999, 0 3px 6px 0 rgba(0,0,0,0.16);
      background-color: #fff;
    }
    `
  },
  body: {
    pad: { horizontal: 'medium', vertical: 'small' },
    border: 'all',
    extend: `
      white-space: nowrap;
    `
  },
  footer: {
    align: 'start',
    border: undefined,
    pad: { horizontal: 'medium', vertical: 'small' },
    verticalAlign: 'bottom'
  },
  extend: `
    background-clip: padding-box;
    th {
      white-space: nowrap;
    }
    tr td {
      background-color: #fff;
    }
    tr:nth-child(even) td {
      background-color: #f2f2f2;
    }
  `
}
