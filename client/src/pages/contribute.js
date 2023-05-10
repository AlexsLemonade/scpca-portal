import React from 'react'
import {
  Box,
  Heading,
  Paragraph,
  Table,
  TableCell,
  TableHeader as GrommetTableHeader,
  TableRow as GrommetTableRow,
  Text
} from 'grommet'
import { MarkdownPage } from 'components/MarkdownPage'
import contributionGuidelines from 'config/contribution-guidelines.md'
import styled from 'styled-components'

const TableHeader = styled(GrommetTableHeader)`
  td {
    padding: 8px;
    white-space: nowrap;
  }
`

const TableRow = styled(GrommetTableRow)`
  box-shadow: none !important;
`

const Button = styled(Box)`
  background: #003595;
  border: none;
  border-radius: 4px;
  display: inline-block;
  color: #fdfdfd;
  cursor: pointer;
  font-size: 16px;
  line-height: 24px;
  padding: 7px 24px;
  &:focus {
    box-shadow: 0 3px 4px 0 rgba(0,0,0,0.5);
  }
  }
`

const headingMargin = { top: '24px', bottom: 'small' }
const listMargin = { bottom: 'medium', horizontal: 'medium' }

export const Contribute = () => {
  const components = {
    h1: {
      component: Heading,
      props: {
        level: 1,
        size: 'xsmall',
        margin: { bottom: '24px' },
        style: { fontWeight: 'normal' }
      }
    },
    h2: {
      component: Heading,
      props: {
        level: 2,
        size: 'xsmall',
        margin: headingMargin,
        weight: 'normal',
        style: { fontWeight: 'normal' }
      }
    },
    h3: {
      component: Heading,
      props: {
        level: 3,
        size: 'small',
        margin: headingMargin
      }
    },
    h4: {
      component: Heading,
      props: {
        level: 4,
        size: 'xsmall',
        margin: headingMargin
      }
    },
    h5: {
      component: Heading,
      props: {
        level: 5,
        size: 'xsmall',
        margin: headingMargin
      }
    },
    ul: {
      component: Box,
      props: {
        as: 'ul',
        margin: listMargin,
        style: { listStyleType: 'disc' }
      }
    },
    ol: {
      component: Box,
      props: {
        as: 'ol',
        margin: listMargin,
        style: { listStyleType: 'decimal' }
      }
    },
    li: {
      component: Text,
      props: { as: 'li', margin: { left: 'medium', vertical: 'xsmall' } }
    },
    p: { component: Paragraph, props: { margin: { bottom: 'medium' } } },
    table: {
      component: Table,
      props: { margin: { bottom: 'small' } }
    },
    thead: { component: TableHeader },
    tr: { component: TableRow },
    td: {
      component: TableCell,
      props: { pad: 'small', style: { whiteSpace: 'normal' } }
    },
    button: {
      component: Button,
      props: {
        as: 'button'
      }
    },
    code: {
      component: Box,
      props: {
        as: 'span',
        background: 'black-tint-90',
        pad: { horizontal: 'xsmall' },
        round: 'xsmall',
        style: { color: '#DB3B28', display: 'inline-block' }
      }
    }
  }

  return (
    <MarkdownPage
      components={components}
      markdown={contributionGuidelines}
      width="960px" // sets the fix width to preserve the UI layout
    />
  )
}

export default Contribute
