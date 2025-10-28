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

// Styles for highlighting rows when their checkbox is selected
const TableRow = styled(GrommetTableRow)`
 ${({ theme }) => css`
   cursor: pointer;
   td {
     vertical-align: middle;
   }
   &.selected {
     > td {
       background: ${theme.global.colors['powder-blue']} !important;
     }
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

export const THead = ({
  instance: {
    headerGroups,
    state: { globalFilter }
  },
  stickies = 0
}) => {
  const [offsets, setOffsets] = useState([])
  const ref = createRef(null)
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
  stickies = 0,
  prevSelectedRows,
  selectedRows
}) => {
  const [offsets, setOffsets] = useState([])
  const ref = createRef(null)
  // Get previously selected modalities for the sample row
  const getPrevSelectedModalities = (id) =>
    Object.keys(prevSelectedRows).filter((m) =>
      prevSelectedRows[m].includes(id)
    )

  // Get currently selected modalities for the sample row
  const getSelectedModalities = (id) =>
    Object.keys(selectedRows).filter((m) => selectedRows[m].includes(id))

  const getClassName = (id) => {
    const prevModalities = getPrevSelectedModalities(id)
    const currModalities = getSelectedModalities(id)

    const isNoneSelected = currModalities.length === 0
    const hasSameModalities =
      prevModalities.length === currModalities.length &&
      prevModalities.every((m) => currModalities.includes(m))

    // No highlight if none selected or all were previously selected
    if (isNoneSelected || hasSameModalities) return ''

    const isNewSelected = currModalities.some(
      (m) => !prevModalities.includes(m)
    )

    return isNewSelected ? 'selected' : ''
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
    // eslint-disable-next-line react/jsx-props-no-spreading
    <TableBody {...getTableBodyProps()}>
      {(page || rows).map((row) => {
        prepareRow(row)
        return (
          <TableRow
            ref={ref}
            className={getClassName(row.original.scpca_id)}
            // eslint-disable-next-line react/jsx-props-no-spreading
            {...row.getRowProps()}
          >
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

// Custom fuzzyText filter function
const fuzzyTextFilterFn = (rows, ids, filterValue) =>
  matchSorter(rows, filterValue, {
    keys: ids.map((id) => `values.${id}`)
  })
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
  const filterTypes = useMemo(
    () => ({
      // Add fuzzyText filter type
      fuzzyText: fuzzyTextFilterFn
    }),
    []
  )
  const columns = useMemo(() => userColumns, [])
  const data = useMemo(() => userData, [])

  const pageSize = initialPageSize || pageSizeOptions[0] || 0

  // if no pageSize is set dont use the hook
  const hooks = [useGlobalFilter, useSortBy]
  if (pageSize !== 0) {
    hooks.push(usePagination)
  }

  const sortRules = useMemo(() => defaultSort, [userData])

  const instance = useTable(
    {
      columns,
      data,
      defaultFilter: 'fuzzyText',
      filterTypes,
      initialState: { pageSize, sortBy: sortRules }
    },
    ...hooks
  )
  const {
    getTableProps,
    state,
    setGlobalFilter,
    globalFilteredRows,
    gotoPage,
    setPageSize,
    pageOptions,
    setHiddenColumns,
    state: { pageIndex }
  } = instance

  userColumns.forEach((c) => {
    // eslint-disable-next-line no-prototype-builtins, no-param-reassign
    if (!c.hasOwnProperty('isVisible')) c.isVisible = true
  })

  useEffect(() => {
    if (instance.rows) {
      onAllRowsChange(instance.rows.map((row) => row.original))
    }
  }, [instance.rows])

  useEffect(() => {
    if (instance.page) {
      onFilteredRowsChange(instance.page.map((row) => row.original))
    }
  }, [instance.page])

  useEffect(() => {
    setHiddenColumns(
      columns
        .filter((column) => !column.isVisible)
        .map((column) => column.accessor)
    )
  }, [setHiddenColumns, columns])

  const hasText = text || (filter && infoText)
  const justify = hasText ? 'between' : 'end'
  const pad = filter ? { vertical: 'medium' } : {}
  const { responsive } = useResponsive()

  const showPageSize =
    pageSizeOptions.length > 0 && data?.length > pageSizeOptions[0]
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
        {text && text}
        {showPageSize && (
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
            pageIndex={state.pageIndex}
            pageSize={state.pageSize}
            totalFilteredSize={globalFilteredRows.length}
          />
        )}
      </Box>
      {children}
      <TableBox width={{ max: 'full' }} overflow="auto" stickies={stickies}>
        {/* eslint-disable-next-line react/jsx-props-no-spreading */}
        <StickyTable {...getTableProps()} width="auto">
          <Head instance={instance} stickies={stickies} />
          <Body
            instance={instance}
            stickies={stickies}
            prevSelectedRows={prevSelectedRows}
            selectedRows={selectedRows}
          />
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
