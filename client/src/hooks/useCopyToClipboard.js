// (resource) https://usehooks-ts.com/react-hook/use-copy-to-clipboard
import { useState } from 'react'

export const useCopyToClipboard = () => {
  const [value, setValue] = useState(null)

  const copyText = async (text) => {
    if (!navigator?.clipboard) {
      // eslint-disable-next-line no-console
      console.warn('Clipboard not supported')
      return false
    }

    try {
      await navigator.clipboard.writeText(text)
      setValue(text)

      return true
    } catch (error) {
      // eslint-disable-next-line no-console
      console.warn('Copy failed', error)
      setValue(null)

      return false
    }
  }

  return [value, copyText]
}
