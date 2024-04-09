import React from 'react'
import { Button } from 'grommet'
import config from 'config'

export const ContributeDownloadPDFButton = () => (
  <Button
    href={config.links.contribute_pdf}
    label="Download Guidelines as PDF"
    target="_blank"
    primary
  />
)

export default ContributeDownloadPDFButton
