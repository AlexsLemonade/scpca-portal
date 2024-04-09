import React from 'react'
import { Button } from 'grommet'
import { links } from 'config'

export const ContributeDownloadPDFButton = () => (
  <Button
    href={links.contributePdf}
    label="Download Guidelines as PDF"
    target="_blank"
    primary
  />
)

export default ContributeDownloadPDFButton
