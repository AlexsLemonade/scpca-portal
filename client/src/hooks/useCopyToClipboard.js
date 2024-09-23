// (resource) https://usehooks-ts.com/react-hook/use-copy-to-clipboard
import { useState } from 'react'

export const useCopyToClipboard = () => {
  const copyText = async (text) => {
    if (!navigator?.clipboard) {
      // eslint-disable-next-line no-console
      console.warn('Clipboard not supported')
      return false
    }

    try {
      await navigator.clipboard.writeText(text)

      return true
    } catch (error) {
      // eslint-disable-next-line no-console
      console.warn('Copy failed', error)

      return false
    }
  }

  return copyText
}
