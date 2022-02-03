import React from 'react'
import {
  Box,
  Paragraph,
  Table,
  TableBody,
  TableCell,
  TableRow,
  Text
} from 'grommet'
import styled from 'styled-components'
import { getBooleanString } from 'helpers/booleanOptions'
import { getReadable } from 'helpers/getReadable'

const DetailsTableDetail = ({ datum, emptyString = 'Not Specified' }) => {
  const { value } = datum

  // true false or null should be treated as booleans
  const bool = getBooleanString(value)
  if (bool !== undefined) return <Text italic={value === null}>{bool}</Text>

  // check if unset, empty string, or empty array
  const isEmpty = !value || value.length === 0
  if (isEmpty) return <Text italic>{emptyString}</Text>

  // check if it is an array of values
  const isArray = Array.isArray(value)
  if (isArray) return <Paragraph>{value.join(', ')}</Paragraph>

  return <Paragraph>{value}</Paragraph>
}

const DetailsTableTable = styled(Table)`
  border: none;
`

const DetailsTableBody = styled(TableBody)`
  border: none;

  > tr > td:first-child {
    width: 150px;
  }

  > tr,
  tr td {
    box-shadow: none;
    white-space: break-spaces;
  }

  > tr:nth-child(2n) td {
    background-color: ${({ theme }) => theme.global.colors.white};
  }

  > tr:nth-child(2n + 1) td {
    background-color: ${({ theme }) =>
      theme.global.colors['background-highlight']};
  }
`

export const DetailsTable = ({ data, order, className }) => {
  const tableData =
    order && typeof data === 'object'
      ? order.map((entry) => {
          // either pass object key or a label value pair
          return typeof entry === 'object'
            ? entry
            : {
                label: getReadable(entry),
                value: data[entry]
              }
        })
      : data

  return (
    <Box width="full">
      <DetailsTableTable className={className}>
        <DetailsTableBody>
          {tableData.map((datum) => (
            <TableRow key={datum.label}>
              <TableCell pad="medium" align="right" verticalAlign="top">
                <Text weight="bold">{datum.label}</Text>
              </TableCell>
              <TableCell pad="medium" align="left">
                <DetailsTableDetail datum={datum} />
              </TableCell>
            </TableRow>
          ))}
        </DetailsTableBody>
      </DetailsTableTable>
    </Box>
  )
}

export default DetailsTable
