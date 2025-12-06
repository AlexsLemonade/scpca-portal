import React, { createContext, useState } from 'react'
import { useHubspotForm } from 'hooks/useHubspotForm'
import { useLocalStorage } from 'hooks/useLocalStorage'
import { api } from 'api'
import { tokenSchema, hubspotSurveySchema, hubspotEmailSchema } from 'schemas'
import { getErrorMessages } from 'helpers/getErrorMessages'

export const ScPCAPortalContext = createContext({})

export const ScPCAPortalContextProvider = ({ children }) => {
  const [browseFilters, setBrowseFilters] = useState({})
  const [email, setEmail] = useLocalStorage('scpca-user-email')
  const [token, setToken] = useLocalStorage('scpca-api-token', false)
  const [acceptsTerms, setAcceptsTerms] = useLocalStorage(
    'scpca-api-terms',
    false
  )
  const [wantsEmails, setWantsEmails] = useLocalStorage(
    'scpca-api-wants-emails',
    false
  )

  const emailListForm = useHubspotForm(
    process.env.HUBSPOT_PORTAL_ID,
    process.env.HUBSPOT_EMAIL_LIST_ID,
    hubspotEmailSchema
  )

  const surveyListForm = useHubspotForm(
    process.env.HUBSPOT_PORTAL_ID,
    process.env.HUBSPOT_SURVEY_LIST_ID,
    hubspotSurveySchema
  )

  const getToken = () => ({
    email,
    is_activated: acceptsTerms
  })

  const validateToken = async () => {
    try {
      await tokenSchema.validate(getToken(), { abortEarly: false })
      return { isValid: true }
    } catch (e) {
      return {
        isValid: false,
        errors: getErrorMessages(e)
      }
    }
  }

  const createToken = async () => {
    const tokenRequest = await api.tokens.create(getToken())

    if (tokenRequest.isOk) {
      setToken(tokenRequest.response.id)
    }

    return tokenRequest
  }

  return (
    <ScPCAPortalContext.Provider
      value={{
        setEmail,
        email,
        token,
        setToken,
        acceptsTerms,
        setAcceptsTerms,
        wantsEmails,
        setWantsEmails,
        createToken,
        validateToken,
        browseFilters,
        setBrowseFilters,
        emailListForm,
        surveyListForm
      }}
    >
      {children}
    </ScPCAPortalContext.Provider>
  )
}
