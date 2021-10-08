import { getReadable } from 'helpers/getReadable'

// convert Yup.js validationError object to error messages object
export const getErrorMessages = (validationError) => {
  const messages = {}
  validationError.inner.forEach(({ path, errors }) => {
    let message = messages
    path.split('.').forEach((attribute, index, arr) => {
      message[attribute] = message[attribute] || {}
      if (index === arr.length - 1) {
        message[attribute] = errors.map((error) =>
          error.replace(path, getReadable(attribute))
        )
      } else {
        message = message[attribute]
      }
    })
  })

  return messages
}

export default getErrorMessages
