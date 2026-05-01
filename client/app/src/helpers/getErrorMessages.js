import { getReadable } from 'helpers/getReadable'

// convert Yup.js validationError object to error messages object
export const getErrorMessages = (validationError) => {
  const messages = {}
  validationError.inner.forEach(({ path, errors }) => {
    path.split('.').forEach((attribute, index, arr) => {
      messages[attribute] = messages[attribute] || {}
      if (index === arr.length - 1) {
        messages[attribute] = errors.map((error) =>
          error.replace(path, getReadable(attribute))
        )
      } else {
        // attach a generic error message when nested error occur
        messages[attribute] = `${getReadable(attribute)} contains errors.`
      }
    })
  })

  return messages
}

export default getErrorMessages
