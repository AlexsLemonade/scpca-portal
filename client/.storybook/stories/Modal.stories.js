import React from 'react'
import Component from 'components/Modal'
import { Button } from 'components/Button'

export default {
  title: 'Components/Modal',
  component: Component
}

export const Default = () => (
  <Component showing title="Test Modal">
    Test content
  </Component>
)

export const WithButton = () => {
  const [showing, setShowing] = React.useState(false)
  return (
    <>
      <Button label="Open Modal" onClick={() => setShowing(true)} />
      <Component showing={showing} setShowing={setShowing} title="Test Modal">
        Test content
      </Component>
    </>
  )
}
