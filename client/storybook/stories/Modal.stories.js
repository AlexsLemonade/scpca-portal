import React from 'react'
import { Modal } from 'components/Modal'
import { Button } from 'components/Button'

export default {
  title: 'Components/Modal'
}

export const Default = () => (
  <Modal showing title="Test Modal">
    Test content
  </Modal>
)

export const WithButton = () => {
  const [showing, setShowing] = React.useState(false)
  return (
    <>
      <Button label="Open Modal" onClick={() => setShowing(true)} />
      <Modal showing={showing} setShowing={setShowing} title="Test Modal">
        Test content
      </Modal>
    </>
  )
}
