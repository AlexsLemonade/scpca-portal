module.exports = () => {
  const isProduction = process.env.VERCEL_GIT_COMMIT_REF === 'master'

  const productionEnv = {
    API_HOST: process.env.API_HOST,
    API_VERSION: process.env.API_VERSION,
    SENTRY_DSN: process.env.SENTRY_DSN,
    SENTRY_ENV: process.env.SENTRY_ENV,
    HUBSPOT_PORTAL_ID: process.env.HUBSPOT_PORTAL_ID,
    HUBSPOT_EMAIL_LIST_ID: process.env.HUBSPOT_EMAIL_LIST_ID
  }

  const stageEnv = {
    API_HOST: process.env.STAGE_API_HOST,
    API_VERSION: process.env.STAGE_API_VERSION,
    SENTRY_DSN: process.env.STAGE_SENTRY_DSN,
    SENTRY_ENV: process.env.STAGE_SENTRY_ENV,
    HUBSPOT_PORTAL_ID: process.env.STAGE_HUBSPOT_PORTAL_ID,
    HUBSPOT_EMAIL_LIST_ID: process.env.STAGE_HUBSPOT_EMAIL_LIST_ID
  }

  const env = isProduction ? productionEnv : stageEnv

  return {
    env
  }
}
