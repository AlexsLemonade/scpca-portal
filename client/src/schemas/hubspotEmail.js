import { string, object } from 'yup'

export default object({
  email: string()
    .email('Please check your email.')
    .required('Please enter your email.')
})
