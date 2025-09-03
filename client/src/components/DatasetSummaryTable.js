import React from 'react'
import {
  Table as GrommetTable,
  TableBody as GrommetTableBody,
  TableCell as GrommentTableCell,
  TableHeader as GrommentTableHeader,
  TableRow,
  Text
} from 'grommet'
import styled from 'styled-components'

const Table = styled(GrommetTable)`
  border: none;
  width: 100%;
  display: table;
`
const TableHeader = styled(GrommentTableHeader)`
  tr td {
    border: none;
    background: #f2f2f2;
    box-shadow: none;
  }
`
const TableBody = styled(GrommetTableBody)`
  border: none;
  tr,
  tr td {
    box-shadow: none;
  }
`

const TableCell = styled(GrommentTableCell)`
  padding-left: 33px;
`

export const DatasetSummaryTable = ({
  data = [],
  columns = [],
  keyValue // Data row property name with unique value across rows
}) => {
  // check the first row to which columns are ints
  const columnAlign = Object.fromEntries(
    columns.map((c) => [
      c,
      Number.isInteger((data[0] || {})[c]) ? 'end' : 'start'
    ])
  )

  return (
    <Table width="100%">
      <TableHeader>
        <TableRow>
          {columns.map((c) => (
            <TableCell
              key={c}
              align={columnAlign[c]}
              pad={columnAlign[c] === 'end' ? { right: '100px' } : ''}
            >
              <Text size="medium">{c}</Text>
            </TableCell>
          ))}
        </TableRow>
      </TableHeader>
      <TableBody>
        {data.map((row) => (
          <TableRow key={row[keyValue]}>
            {columns.map((c) => (
              <TableCell
                key={`${row[keyValue]}-${c}`}
                align={columnAlign[c]}
                pad={columnAlign[c] === 'end' ? { right: '100px' } : ''}
              >
                <Text>{row[c]}</Text>
              </TableCell>
            ))}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
