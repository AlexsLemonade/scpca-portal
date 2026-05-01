import { string, object, date } from 'yup'

export const hubspotSurveySchema = object({
  email: string()
    .email('Please check your email.')
    .required('Please enter your email.'),
  scpca_last_download_date: date('Please format your date correctly').required(
    'Please enter the last download date'
  )
})

export default hubspotSurveySchema
