import React from 'react'
import { Download } from 'components/Download'
import project from '../data/project'

export default {
  title: 'Components/Download',
  args: { computedFile: project.computed_file }
}

export const Default = (args) => <Download computedFile={args.computedFile} />
