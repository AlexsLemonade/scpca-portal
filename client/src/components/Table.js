import React, { useState, useEffect, createRef, useMemo } from 'react'
import {
  Box,
  Button,
  Text,
  Table as GrommetTable,
  TableBody,
  TableCell,
  TableHeader as GrommetTableHeader,
  TableRow as GrommetTableRow
} from 'grommet'
import styled, { css } from 'styled-components'
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  flexRender
} from '@tanstack/react-table'
import { matchSorter } from 'match-sorter'
import { Icon } from 'components/Icon'
import { TableFilter } from 'components/TableFilter'
import { TablePageSize } from 'components/TablePageSize'
import { Pagination } from 'components/Pagination'
import { InfoText } from 'components/InfoText'
import { useResponsive } from 'hooks/useResponsive'

// Styles for highlighting rows when their checkbox is selected
const TableRow = styled(GrommetTableRow)`
  cursor: pointer;
  td {
    vertical-align: middle;
  }
 ${({ highlighted, theme }) =>
   highlighted &&
   css`
     > td {
       background: ${theme.global.colors['powder-blue']} !important;
     }
   `}}
`

// Styles to allow for dynamic "sticky" columns
const TableBox = styled(Box)`
  position: relative;
  ${({ stickies }) =>
    stickies > 0 &&
    css`
      overflow: auto;
    `}
`

const TableHeader = styled(GrommetTableHeader)`
  th {
    vertical-align: middle;
  }
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

export const THead = ({ instance, stickies = 0 }) => {
  const [offsets, setOffsets] = useState([])
  const ref = createRef(null)
  const { globalFilter } = instance.getState()

  useEffect(() => {
    const nodes = Array.from(ref.current.childNodes)
    const widths = nodes.map((n) => n.clientWidth)
    const newOffsets = widths
      .map((_, i) => widths.slice(0, i).reduce((a, b) => a + b, 0))
      .slice(0, stickies)
    setOffsets(newOffsets)
  }, [globalFilter, stickies])

  return (
    <TableHeader>
      {instance.getHeaderGroups().map((headerGroup) => (
        <TableRow ref={ref} key={headerGroup.id}>
          {headerGroup.headers.map((header, index) => (
            <StickyTableCell
              scope="col"
              key={header.id}
              offset={offsets[index]}
              stickies={stickies}
              index={index}
              onClick={header.column.getToggleSortingHandler()}
            >
              <Box direction="row" justify="between">
                {flexRender(
                  header.column.columnDef.header,
                  header.getContext()
                )}
                {header.column.getCanSort() && (
                  <SortIcon
                    sorted={!!header.column.getIsSorted()}
                    descending={header.column.getIsSorted() === 'desc'}
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
  instance,
  stickies = 0,
  prevSelectedRows,
  selectedRows,
  pageRows
}) => {
  const [offsets, setOffsets] = useState([])
  const ref = createRef(null)
  const { globalFilter } = instance.getState()

  const getIsHighlighted = (id) => {
    // Previously selected modalities for the sample row
    const prevModalities = Object.keys(prevSelectedRows).filter((m) =>
      prevSelectedRows[m].includes(id)
    )
    // Currently selected modalities for the sample row
    const currModalities = Object.keys(selectedRows).filter((m) =>
      selectedRows[m].includes(id)
    )

    return currModalities.some((m) => !prevModalities.includes(m))
  }

  useEffect(() => {
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
    <TableBody>
      {pageRows.map((row) => (
        <TableRow
          ref={ref}
          key={row.id}
          highlighted={getIsHighlighted(row.original.scpca_id)}
        >
          {row.getVisibleCells().map((cell, index) => (
            <StickyTableCell
              key={cell.id}
              offset={offsets[index]}
              stickies={stickies}
              index={index}
            >
              {flexRender(cell.column.columnDef.cell, cell.getContext())}
            </StickyTableCell>
          ))}
        </TableRow>
      ))}
    </TableBody>
  )
}

// Custom fuzzyText filter function
// TODO: determine if we still want to use matchSorter as react table v8
// enforces a fuzzy function acting on one row at a time
const fuzzyTextFilterFn = (row, columnId, filterValue) => {
  const value = row.getValue(columnId)
  return matchSorter([value], filterValue).length > 0
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
  defaultSort = [],
  pageSize: initialPageSize = 0,
  pageSizeOptions = [],
  prevSelectedRows = {}, // For unhighlithing previously selected sample rows
  selectedRows = {}, // For highlighting currently selected samples rows
  infoText = '',
  text = '',
  children,
  onAllRowsChange = () => {},
  onFilteredRowsChange = () => {}
}) => {
  const columns = useMemo(() => userColumns, [])
  const data = useMemo(() => userData, [])

  const pageSize = initialPageSize || pageSizeOptions[0] || 0

  const [globalFilter, setGlobalFilter] = useState('')
  const [sorting, setSorting] = useState(defaultSort)
  const [pagination, setPagination] = useState({ pageIndex: 0, pageSize })
  const [columnVisibility, setColumnVisibility] = useState(
    Object.fromEntries(
      userColumns.map((c) => [c.accessorKey ?? c.id, c.isVisible ?? true])
    )
  )

  const instance = useReactTable({
    columns,
    data,
    filterFns: { fuzzyText: fuzzyTextFilterFn },
    globalFilterFn: 'fuzzyText',
    state: {
      globalFilter,
      sorting,
      pagination,
      columnVisibility
    },
    onGlobalFilterChange: setGlobalFilter,
    onSortingChange: setSorting,
    onPaginationChange: setPagination,
    onColumnVisibilityChange: setColumnVisibility,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel()
  })

  const state = instance.getState()
  const pageRows =
    pageSize !== 0
      ? instance.getPaginationRowModel().rows
      : instance.getSortedRowModel().rows

  const gotoPage = (index) => setPagination((p) => ({ ...p, pageIndex: index }))
  const setPageSize = (size) => setPagination({ pageIndex: 0, pageSize: size })

  useEffect(() => {
    const { rows } = instance.getCoreRowModel()
    if (rows.length > 0) {
      onAllRowsChange(rows.map((row) => row.original))
    }
  }, [data])

  useEffect(() => {
    if (pageRows.length > 0) {
      onFilteredRowsChange(pageRows.map((row) => row.original))
    }
  }, [globalFilter, pagination])

  const hasText = text || (filter && infoText)
  const justify = hasText ? 'between' : 'end'
  const pad = filter ? { vertical: 'medium' } : {}
  const { responsive } = useResponsive()

  const showPageSize =
    pageSizeOptions.length > 0 && data?.length > pageSizeOptions[0]
  const showPagination = pageSize !== 0 && instance.getPageCount() > 1

  const filteredRowCount = instance.getFilteredRowModel().rows.length

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
        {text && text}
        {showPageSize && (
          <TablePageSize
            pageSize={state.pagination.pageSize}
            setPageSize={setPageSize}
            pageSizeOptions={pageSizeOptions}
            gotoPage={gotoPage}
          />
        )}
        {filter && (
          <TableFilter
            // state.globalFilter is the current string being filtered against
            globalFilter={globalFilter}
            setGlobalFilter={setGlobalFilter}
            pageIndex={state.pagination.pageIndex}
            pageSize={state.pagination.pageSize}
            totalFilteredSize={filteredRowCount}
          />
        )}
      </Box>
      {children}
      <TableBox width={{ max: 'full' }} overflow="auto" stickies={stickies}>
        <StickyTable width="auto">
          <Head instance={instance} stickies={stickies} />
          <Body
            instance={instance}
            stickies={stickies}
            prevSelectedRows={prevSelectedRows}
            selectedRows={selectedRows}
            pageRows={pageRows}
          />
        </StickyTable>
      </TableBox>
      {filter && filteredRowCount === 0 && (
        <Box
          direction="row"
          align="center"
          justify="center"
          gap="medium"
          pad={{ vertical: 'large' }}
        >
          <Text italic>Filter has no matches.</Text>
          <Button label="Reset Filter" onClick={() => setGlobalFilter('')} />
        </Box>
      )}
      {showPagination && (
        <Box justify="center" pad={{ vertical: 'medium' }}>
          <Pagination
            update={({ pageIndex: index }) => gotoPage(index)}
            offset={state.pagination.pageIndex * state.pagination.pageSize}
            limit={state.pagination.pageSize}
            count={filteredRowCount}
          />
        </Box>
      )}
    </>
  )
}

export default Table
