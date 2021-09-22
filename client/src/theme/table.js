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
    border: undefined,
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
    th {
      white-space: nowrap;
    }
    tr {
      box-shadow: 1px 0 0 0 #ccc, 0 1px 0 0 #ccc;
    }
    tr td, tr th {
      background-color: #fff;
      box-shadow: 1px 0 0 0 #ccc inset, 0 1px 0 0 #ccc inset;
    }
    tr:nth-child(even) td {
      background-color: #f2f2f2;
    }
  `
}
