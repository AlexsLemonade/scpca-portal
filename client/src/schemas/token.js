import { boolean, string, object } from 'yup'

export const schema = object({
  email: string().required().email('Please check your email.'),
  is_activated: boolean()
    .required()
    .oneOf([true], 'Please accept the terms of service.')
})

export default schema
