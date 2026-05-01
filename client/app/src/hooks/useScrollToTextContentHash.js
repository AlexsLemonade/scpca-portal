import { useEffect } from 'react'
import { slugify } from 'helpers/slugify'
import { getHash } from 'helpers/getHash'

// This hook takes the following params:
// - ref: a DOM ref
// - selector: css selector for the querySelectorAll method
// - y: (optional) y-coordinate for the scrollBy method, -90 by default
// If there is a match (a slug version of textContent (for id name) matching a hash in URL),
// it will scroll to the element with that id name on page load

export const useScrollToTextContentHash = (ref, selector, y = -90) => {
  const slug = getHash().replace('#', '')

  useEffect(() => {
    if (!ref.current || !slug) return

    const sections = ref.current.querySelectorAll(selector)

    const section = Array.from(sections).find(
      (node) => slug === slugify(node.textContent)
    )

    if (!section) return

    section.scrollIntoView(true)
    window.scrollBy(0, y)
  }, [ref, selector])
}
