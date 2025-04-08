import React from 'react'
import {
  Table,
  TableBody,
  TableCell,
  TableHeader,
  TableRow,
  Text
} from 'grommet'
import styled from 'styled-components'

const StyledTable = styled(Table)`
  border: none;
  width: 100%;
  display: table;
`
const StyledTableHeader = styled(TableHeader)`
  tr td {
    border: none;
    background: #f2f2f2;
    box-shadow: none;
  }
`
const StyledTableBody = styled(TableBody)`
  border: none;
  tr,
  tr td {
    box-shadow: none;
  }
`

const StyledTableCell = styled(TableCell)`
  padding-left: 33px;
`

export const DatasetSummaryTable = ({ data = [], columns = [] }) => {
  // check the first row to which columns are ints
  const columnAlign = Object.fromEntries(
    columns.map((c) => [
      c,
      Number.isInteger((data[0] || {})[c]) ? 'end' : 'start'
    ])
  )

  return (
    <StyledTable width="100%">
      <StyledTableHeader>
        <TableRow>
          {columns.map((c) => (
            <StyledTableCell
              align={columnAlign[c]}
              pad={columnAlign[c] === 'end' ? { right: '100px' } : ''}
            >
              <Text size="medium">{c}</Text>
            </StyledTableCell>
          ))}
        </TableRow>
      </StyledTableHeader>
      <StyledTableBody>
        {data.map((row) => (
          <TableRow>
            {columns.map((c) => (
              <StyledTableCell
                align={columnAlign[c]}
                pad={columnAlign[c] === 'end' ? { right: '100px' } : ''}
              >
                <Text>{row[c]}</Text>
              </StyledTableCell>
            ))}
          </TableRow>
        ))}
      </StyledTableBody>
    </StyledTable>
  )
}
