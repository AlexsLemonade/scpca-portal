// (resource) https://usehooks-ts.com/react-hook/use-copy-to-clipboard
import { useState } from 'react'

export const useCopyToClipboard = () => {
  const [value, setValue] = useState(null)

  const copyText = async (text) => {
    if (!navigator?.clipboard) {
      console.warn('Clipboard not supported')
      return false
    }

    try {
      await navigator.clipboard.writeText(text)
      setValue(text)

      return true
    } catch (error) {
      console.warn('Copy failed', error)
      setValue(null)

      return false
    }
  }

  return [value, copyText]
}
