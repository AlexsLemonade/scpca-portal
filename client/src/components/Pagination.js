import React from 'react'
import { Box, Button, Paragraph, Text, TextInput } from 'grommet'
import { FormPrevious, FormNext } from 'grommet-icons'
import {
  offsetToPage,
  pageToOffset,
  countToLastOffset
} from 'helpers/getPagination'

export const Pagination = ({
  update,
  offset: initialOffset,
  limit,
  count,
  scroll = false
}) => {
  const [offset, setOffset] = React.useState(initialOffset)
  const [enteredPageNumber, setEnteredPageNumber] = React.useState('')
  const [enteredPageNumberInRange, setEnteredPageNumberInRange] =
    React.useState(false)
  const last = countToLastOffset(count, limit)

  React.useEffect(() => {
    if (initialOffset !== offset) setOffset(initialOffset)
  }, [initialOffset])

  const atStart = offset === 0
  const atEnd = offset === last

  const handlePageNumberRequest = ({ target: { value } }) => {
    if (value === '') setEnteredPageNumber('')

    const newOffset = pageToOffset(value, limit)
    const inRange = newOffset <= last && newOffset >= 0
    setEnteredPageNumberInRange(inRange)
    setEnteredPageNumber(value)
  }

  const updateOffset = (newOffset) => {
    update({
      offset: newOffset,
      pageIndex: offsetToPage(newOffset, limit) - 1
    })
    setOffset(newOffset)
    setEnteredPageNumber('')
    if (scroll) {
      // scroll to top of page changing page
      window.scrollTo({
        top: 0
      })
    }
  }

  const goToOffsetRequest = () => {
    updateOffset(pageToOffset(parseInt(enteredPageNumber, 10), limit))
  }

  const [buttonOffsets, setButtonOffsets] = React.useState([])

  React.useEffect(() => {
    const page = offsetToPage(offset, limit)
    const lastPage = offsetToPage(last, limit)
    const allOffsets = [...Array(lastPage).keys()].map((o) => o * limit)
    // get first 6
    if (page <= 2) setButtonOffsets(allOffsets.slice(0, 6))
    // get last 5
    else if (lastPage - page <= 2) setButtonOffsets(allOffsets.slice(-5))
    // get 2 before and 2 after current
    else setButtonOffsets(allOffsets.slice(page - 2, page + 3))
  }, [offset, limit])

  return (
    <Box
      pad={{ bottom: 'gutter' }}
      direction="row"
      gap="gutter"
      align="center"
      alignSelf="center"
    >
      <Box direction="row" gap="6px">
        <Button
          plain
          gap="xxsmall"
          width="small"
          label="Previous"
          aria-label="Previous"
          icon={<FormPrevious color={atStart ? 'black-tint-60' : 'brand'} />}
          disabled={atStart}
          onClick={() => updateOffset(offset - limit)}
        />
        {!buttonOffsets.includes(0) && [
          <Button
            plain
            key="start"
            pad="xsmall"
            onClick={() => updateOffset(0)}
          >
            <Text color="brand">1</Text>
          </Button>,
          !buttonOffsets.includes(pageToOffset(2, limit)) && (
            <Paragraph
              key="elipse-start"
              size="medium"
              margin="none"
              color="black-tint-60"
            >
              ...
            </Paragraph>
          )
        ]}
        {buttonOffsets.map((pageOffset) =>
          offset !== pageOffset ? (
            <Button
              key={pageOffset}
              plain
              onClick={() => updateOffset(pageOffset)}
            >
              <Text color="brand">{offsetToPage(pageOffset, limit)}</Text>
            </Button>
          ) : (
            <Paragraph
              key="current-page"
              size="medium"
              margin="none"
              color="black"
            >
              {offsetToPage(pageOffset, limit)}
            </Paragraph>
          )
        )}
        {!buttonOffsets.includes(last) && [
          !buttonOffsets.includes(last - limit) && (
            <Paragraph
              key="elipse-end"
              size="medium"
              margin="none"
              color="black-tint-60"
            >
              ...
            </Paragraph>
          ),
          <Button
            plain
            key={last}
            pad="xsmall"
            onClick={() => updateOffset(last)}
          >
            <Text color="brand">{offsetToPage(last, limit)}</Text>
          </Button>
        ]}
        <Button
          plain
          reverse
          gap="xxsmall"
          width="small"
          label="Next"
          aria-label="Next"
          icon={<FormNext color={atEnd ? 'black-tint-60' : 'brand'} />}
          disabled={atEnd}
          onClick={() => updateOffset(offset + limit)}
        />
      </Box>
      <Box direction="row" align="center" gap="small">
        <Paragraph size="medium" margin="none" color="black">
          Jump to page
        </Paragraph>{' '}
        <Box width="xsmall">
          <TextInput
            type="number"
            min="1"
            max={offsetToPage(last, limit)}
            size="medium"
            value={enteredPageNumber}
            aria-label="Jump to page"
            onChange={handlePageNumberRequest}
          />
        </Box>
        <Button
          label="Go"
          aria-label="Go"
          disabled={!enteredPageNumberInRange || enteredPageNumber === ''}
          onClick={goToOffsetRequest}
        />
      </Box>
    </Box>
  )
}

export default Pagination
