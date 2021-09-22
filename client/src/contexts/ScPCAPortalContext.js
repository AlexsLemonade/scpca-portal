import React from 'react'
import { useLocalStorage } from 'hooks/useLocalStorage'
import api from 'api'
import tokenSchema from 'schemas/token'

export const ScPCAPortalContext = React.createContext({})

export const ScPCAPortalContextProvider = ({ children }) => {
  const [email, setEmail] = useLocalStorage('scpca-token-email')
  const [token, setToken] = useLocalStorage('scpca-api-token', false)
  const [acceptsTerms, setAcceptsTerms] = useLocalStorage('scpca-api-terms')
  const [wantsEmails, setWantsEmails] = useLocalStorage(
    'scpca-api-wants-emails'
  )
  // const [signedUpForEmails, setSignedUpForEmails] = useLocalStorage(
  //  'scpca-api-token'
  // )

  const getToken = () => ({
    email,
    is_activated: acceptsTerms
  })

  // const signUpForEmails = async () => {
  //  // probably shouldnt use the api for this
  //  // maybe helpers?
  // }

  const validateToken = async () => {
    try {
      await tokenSchema.validate(getToken())
      return { isValid: true }
    } catch ({ errors }) {
      return {
        isValid: false,
        errors
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
        validateToken
      }}
    >
      {children}
    </ScPCAPortalContext.Provider>
  )
}
