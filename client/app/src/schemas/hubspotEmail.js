import { string, object } from 'yup'

export const hubspotEmailSchema = object({
  email: string()
    .email('Please check your email.')
    .required('Please enter your email.')
})

export default hubspotEmailSchema
