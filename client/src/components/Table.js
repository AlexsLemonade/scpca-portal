import React from 'react'
import {
  Box,
  Button,
  Text,
  Table as GrommetTable,
  TableRow,
  TableBody,
  TableCell,
  TableHeader
} from 'grommet'
import styled, { css } from 'styled-components'
import {
  useTable,
  useSortBy,
  useGlobalFilter,
  usePagination
} from 'react-table'
import { matchSorter } from 'match-sorter'
import { Icon } from 'components/Icon'
import { TableFilter } from 'components/TableFilter'
import { TablePageSize } from 'components/TablePageSize'
import { Pagination } from 'components/Pagination'
import { InfoText } from 'components/InfoText'
import { useResponsive } from 'hooks/useResponsive'

// Styles to allow for dynamic "sticky" columns
const TableBox = styled(Box)`
  position: relative;
  ${({ stickies }) =>
    stickies > 0 &&
    css`
      overflow: auto;
    `}
`

const StickyTable = styled(GrommetTable)`
  position: relative;
  table-layout: auto;
  border-collapse: separate;
  border-spacing: 0;
`

const StickyTableCell = styled(TableCell)`
  ${({ offset, index }) =>
    typeof offset === 'number' &&
    css`
      left: ${offset + 2}px;
      position: sticky;
      z-index: 2;
      border-left: 1px solid #ccc;
      box-sizing: border-box;
      margin-right: ${index}px;
      &:first-child {
        left: 0;
        &:after {
          border-top: 1px solid #ccc;
          content: '';
          display: block;
          z-index: 1;
          background-color: #fff;
          position: absolute;
          top: 0;
          right: -2px;
          bottom: 0;
          width: 2px;
        }
      }
    `}
  ${({ stickies, index }) =>
    stickies - 1 === index &&
    css`
      border-right: 1px solid #ccc;
      box-shadow: 1px 0 0 0 #ccc inset, 0 1px 0 0 #ccc inset,
        3px 0px 6px 0 rgba(0, 0, 0, 0.1) !important;
    `}
`

const SortIcon = ({ sorted, descending }) => {
  const color = sorted ? 'brand' : 'black-tint-60'
  const upColor = !descending ? color : 'black-tint-60'
  const downColor = descending ? color : 'black-tint-60'
  return (
    <Box pad={{ left: 'small' }}>
      <Icon name="ChevronUp" size="small" color={upColor} />
      <Icon name="ChevronDown" size="small" color={downColor} />
    </Box>
  )
}

export const THead = ({
  instance: {
    headerGroups,
    state: { globalFilter }
  },
  stickies = 0
}) => {
  const [offsets, setOffsets] = React.useState([])
  const ref = React.createRef(null)
  React.useEffect(() => {
    const nodes = Array.from(ref.current.childNodes)
    const widths = nodes.map((n) => n.clientWidth)
    const newOffsets = widths
      .map((_, i) => widths.slice(0, i).reduce((a, b) => a + b, 0))
      .slice(0, stickies)
    setOffsets(newOffsets)
  }, [globalFilter, stickies])
  return (
    <TableHeader>
      {headerGroups.map((headerGroup) => (
        // eslint-disable-next-line react/jsx-props-no-spreading
        <TableRow ref={ref} {...headerGroup.getHeaderGroupProps()}>
          {headerGroup.headers.map((column, index) => (
            // eslint-disable-next-line react/jsx-props-no-spreading
            <StickyTableCell
              scope="col"
              offset={offsets[index]}
              stickies={stickies}
              index={index}
              // eslint-disable-next-line react/jsx-props-no-spreading
              {...column.getHeaderProps(column.getSortByToggleProps())}
            >
              <Box direction="row" justify="between">
                {column.render('Header')}
                {column.canSort && (
                  <SortIcon
                    sorted={column.isSorted}
                    descending={column.isSortedDesc}
                  />
                )}
              </Box>
            </StickyTableCell>
          ))}
        </TableRow>
      ))}
    </TableHeader>
  )
}

export const TBody = ({
  instance: {
    getTableBodyProps,
    prepareRow,
    page,
    rows,
    state: { globalFilter }
  },
  stickies = 0
}) => {
  const [offsets, setOffsets] = React.useState([])
  const ref = React.createRef(null)
  React.useEffect(() => {
    if (ref.current) {
      const nodes = Array.from(ref.current.childNodes)
      const widths = nodes.map((n) => n.clientWidth)
      const newOffsets = widths
        .map((_, i) => widths.slice(0, i).reduce((a, b) => a + b, 0))
        .slice(0, stickies)
      setOffsets(newOffsets)
    }
  }, [globalFilter, stickies])
  return (
    // eslint-disable-next-line react/jsx-props-no-spreading
    <TableBody {...getTableBodyProps()}>
      {(page || rows).map((row) => {
        prepareRow(row)
        return (
          // eslint-disable-next-line react/jsx-props-no-spreading
          <TableRow ref={ref} {...row.getRowProps()}>
            {row.cells.map((cell, index) => (
              <StickyTableCell
                offset={offsets[index]}
                stickies={stickies}
                index={index}
                // eslint-disable-next-line react/jsx-props-no-spreading
                {...cell.getCellProps()}
              >
                {cell.render('Cell')}
              </StickyTableCell>
            ))}
          </TableRow>
        )
      })}
    </TableBody>
  )
}

const fuzzyTextFilterFn = (rows, ids, filterValue) => {
  return matchSorter(rows, filterValue, {
    keys: ids.map((id) => `values.${id}`)
  })
}

// Let the table remove the filter if the string is empty
fuzzyTextFilterFn.autoRemove = (val) => !val

export const Table = ({
  columns: userColumns,
  data: userData,
  stickies = 0,
  Head = THead,
  Body = TBody,
  filter = false,
  pageSize: initialPageSize = 0,
  pageSizeOptions = [],
  infoText
}) => {
  const globalFilter = 'fuzzyText'
  const filterTypes = React.useMemo(
    () => ({
      // Add a new fuzzyTextFilterFn filter type.
      fuzzyText: fuzzyTextFilterFn
    }),
    []
  )
  const columns = React.useMemo(() => userColumns, [])
  const data = React.useMemo(() => userData, [])

  const pageSize = initialPageSize || pageSizeOptions[0] || 0

  // if no pageSize is set dont use the hook
  const hooks = [useGlobalFilter, useSortBy]
  if (pageSize !== 0) {
    hooks.push(usePagination)
  }

  const instance = useTable(
    {
      columns,
      data,
      globalFilter,
      filterTypes,
      initialState: { pageSize }
    },
    ...hooks
  )
  const {
    getTableProps,
    state,
    setGlobalFilter,
    globalFilteredRows,
    preGlobalFilteredRows,
    gotoPage,
    setPageSize,
    pageOptions,
    state: { pageIndex }
  } = instance

  const justify = filter && infoText ? 'between' : 'end'
  const pad = filter ? { vertical: 'medium' } : {}
  const { responsive } = useResponsive()

  const showPagination = pageOptions && pageOptions.length > 1

  return (
    <>
      <Box
        direction={responsive('column', 'row')}
        pad={pad}
        gap="medium"
        align="start"
        justify={justify}
      >
        {infoText && <InfoText label={infoText} />}
        {pageSizeOptions.length > 0 && (
          <TablePageSize
            pageSize={state.pageSize}
            setPageSize={setPageSize}
            pageSizeOptions={pageSizeOptions}
            gotoPage={gotoPage}
          />
        )}
        {filter && (
          <TableFilter
            // state.globalFilter is the current string being filtered against
            globalFilter={state.globalFilter}
            setGlobalFilter={setGlobalFilter}
            globalFilteredRows={globalFilteredRows}
            preGlobalFilteredRows={preGlobalFilteredRows}
          />
        )}
      </Box>
      <TableBox width={{ max: 'full' }} overflow="auto" stickies={stickies}>
        {/* eslint-disable-next-line react/jsx-props-no-spreading */}
        <StickyTable {...getTableProps()} width="auto">
          <Head instance={instance} stickies={stickies} />
          <Body instance={instance} stickies={stickies} />
        </StickyTable>
      </TableBox>
      {filter && globalFilteredRows.length === 0 && (
        <Box
          direction="row"
          align="center"
          justify="center"
          gap="medium"
          pad={{ vertical: 'large' }}
        >
          <Text italic>Filter has no matches.</Text>
          <Button label="Reset Filter" onClick={() => setGlobalFilter()} />
        </Box>
      )}
      {showPagination && (
        <Box justify="center" pad={{ vertical: 'medium' }}>
          <Pagination
            update={({ pageIndex: index }) => gotoPage(index)}
            offset={pageIndex * state.pageSize}
            limit={state.pageSize}
            count={globalFilteredRows.length}
          />
        </Box>
      )}
    </>
  )
}

export default Table
