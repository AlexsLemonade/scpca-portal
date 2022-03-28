import { useState } from 'react'
import { request } from 'helpers/request'
import { getErrorMessages } from 'helpers/getErrorMessages'
import { useLocalStorage } from 'hooks/useLocalStorage'

export const useHubspotForm = (portalId, formId, formSchema) => {
  const [formData, setFormData] = useState({})
  const [errors, setErrors] = useState({})
  const [success, setSuccess] = useLocalStorage(formId, false)

  const apiBase = 'https://api.hsforms.com/submissions/v3/integration/submit'
  const endpoint = `${apiBase}/${portalId}/${formId}`

  const getAttribute = (attribute) => formData[attribute]

  const setAttribute = (attribute, value) => {
    resetError(attribute)
    const newFormData = { ...formData }
    newFormData[attribute] = value
    setFormData(newFormData)
  }

  // helper for slowly removing errors from the error obj
  const resetError = (attribute) => {
    if (attribute in errors) {
      const newErrors = { ...errors }
      delete newErrors[attribute]
      setErrors(newErrors)
    }
  }

  // take a schema from /schemas test it and set errors from helper
  // call this before submit()
  const validate = async (schema = formSchema) => {
    try {
      await schema.validate(formData, { abortEarly: false })
    } catch (e) {
      const errorMessages = getErrorMessages(e)
      setErrors(errorMessages)
      return { isValid: false, errors: errorMessages }
    }

    return { isValid: true }
  }

  // can't just post the json data, no that would be too easy
  // convert to {fields: [{name, value}]}
  const submit = async (submitData = formData) => {
    const fields = Object.entries(submitData).map(([name, value]) => ({
      name,
      value
    }))
    const formRequest = await request(endpoint, {
      method: 'POST',
      body: JSON.stringify({ fields })
    })
    setSuccess(formRequest.isOk)
    return formRequest
  }

  // helper for knowing when to disable the button
  const hasError = Object.keys(errors).length !== 0

  return {
    getAttribute,
    setAttribute,
    submit,
    validate,
    errors,
    hasError,
    success
  }
}

export default useHubspotForm
