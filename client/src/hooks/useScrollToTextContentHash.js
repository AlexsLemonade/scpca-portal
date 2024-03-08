import { useEffect } from 'react'
import { slugify } from 'helpers/slugify'
import { getHash } from 'helpers/getHash'

// Given the hook is loaded with a hash ie. #some-slug
// This hook will take a DOM ref and css selector
// Will iterator over matches and check textContent
// If there is a match it will scroll to that element

export const useScrollToTextContentHash = (ref, selector) => {
  const slug = getHash().replace('#', '')

  useEffect(() => {
    if (!ref.current || !slug) return

    const sections = ref.current.querySelectorAll(selector)

    const section = Array.from(sections).find(
      (node) => slug === slugify(node.textContent)
    )

    if (!section) return

    section.scrollIntoView(true)
    window.scrollBy(0, -90)
  }, [ref, selector])
}
