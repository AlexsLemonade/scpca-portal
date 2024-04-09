import React from 'react'
import {
  Box,
  Heading,
  Table,
  TableCell,
  TableHeader as GrommetTableHeader,
  TableRow as GrommetTableRow,
  Text
} from 'grommet'
import { Button } from 'components/Button'
import { ContributeDownloadPDFButton } from 'components/ContributeDownloadPDFButton'
import { Link } from 'components/Link'
import { MarkdownPage } from 'components/MarkdownPage'
import config from 'config'
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

const IntakeFormLink = () => (
  <Button
    href={config.links.contribute_hsform}
    label="Complete the Intake Form"
    margin={{ top: 'small', bottom: 'medium' }}
    target="_blank"
    primary
  />
)

export const Contribute = () => {
  const headingMargin = { top: '24px', bottom: 'small' }
  const listMargin = { bottom: 'medium', horizontal: 'medium' }

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
    IntakeFormLink: {
      component: IntakeFormLink
    },
    a: {
      component: Link
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
    table: {
      component: Table,
      props: { margin: { bottom: 'small' } }
    },
    thead: { component: TableHeader },
    tr: { component: TableRow },
    td: {
      component: TableCell,
      props: { pad: 'small', style: { whiteSpace: 'normal' } }
    }
  }

  return (
    <>
      <Box alignSelf="end" margin={{ top: 'large' }}>
        <ContributeDownloadPDFButton />
      </Box>
      <MarkdownPage
        components={components}
        markdown={contributionGuidelines}
        width="xlarge"
      />
    </>
  )
}

export default Contribute
