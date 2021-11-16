import { string, object } from 'yup'

export const schema = object({
  email: string()
    .email('Please check your email.')
    .required('Please enter your email.')
})

export default schema
