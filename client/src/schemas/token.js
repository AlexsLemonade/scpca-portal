import { boolean, string, object } from 'yup'

export default object({
  email: string().email('Please check your email.'),
  is_activated: boolean().oneOf([true], 'Please accept the terms of service.')
})
