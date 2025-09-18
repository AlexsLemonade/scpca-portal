const path = require('path')

module.exports = () => {
  const isProduction = process.env.VERCEL_GIT_COMMIT_REF === 'main'

  // eslint-disable-next-line prettier/prettier, no-console
  console.log(
    'CCDL BUILD LOG:',
    process.env.VERCEL_GIT_COMMIT_REF,
    isProduction
  )

  const productionEnv = {
    API_HOST: process.env.API_HOST,
    API_VERSION: process.env.API_VERSION,
    SENTRY_DSN: process.env.SENTRY_DSN,
    SENTRY_ENV: process.env.SENTRY_ENV,
    HUBSPOT_PORTAL_ID: process.env.HUBSPOT_PORTAL_ID,
    HUBSPOT_EMAIL_LIST_ID: process.env.HUBSPOT_EMAIL_LIST_ID,
    HUBSPOT_SURVEY_LIST_ID: process.env.HUBSPOT_SURVEY_LIST_ID,
    PRIVACY_POLICY_RELEASE: process.env.PRIVACY_POLICY_RELEASE,
    TOS_RELEASE: process.env.TOS_RELEASE,
    BANNER_STATE: process.env.BANNER_STATE,
    BANNER_CONTENT: process.env.BANNER_CONTENT,
    CONTRIBUTIONS_OPEN: process.env.CONTRIBUTIONS_OPEN,
    CLIENT_SECRET: process.env.CLIENT_SECRET,
    CELLBROWSER_SECRET: process.env.CELLBROWSER_SECRET,
    CELLBROWSER_STATIC_HOST: process.env.CELLBROWSER_STATIC_HOST,
  }

  const stageEnv = {
    API_HOST: process.env.STAGE_API_HOST,
    API_VERSION: process.env.STAGE_API_VERSION,
    SENTRY_DSN: process.env.STAGE_SENTRY_DSN,
    SENTRY_ENV: process.env.STAGE_SENTRY_ENV,
    HUBSPOT_PORTAL_ID: process.env.STAGE_HUBSPOT_PORTAL_ID,
    HUBSPOT_EMAIL_LIST_ID: process.env.STAGE_HUBSPOT_EMAIL_LIST_ID,
    HUBSPOT_SURVEY_LIST_ID: process.env.STAGE_HUBSPOT_SURVEY_LIST_ID,
    PRIVACY_POLICY_RELEASE: process.env.STAGE_PRIVACY_POLICY_RELEASE,
    TOS_RELEASE: process.env.STAGE_TOS_RELEASE,
    BANNER_STATE: process.env.STAGE_BANNER_STATE,
    BANNER_CONTENT: process.env.STAGE_BANNER_CONTENT,
    CONTRIBUTIONS_OPEN: process.env.STAGE_CONTRIBUTIONS_OPEN,
    CLIENT_SECRET: process.env.STAGE_CLIENT_SECRET,
    CELLBROWSER_SECRET: process.env.STAGE_CELLBROWSER_SECRET,
    CELLBROWSER_STATIC_HOST: process.env.STAGE_CELLBROWSER_STATIC_HOST,
  }

  const env = isProduction ? productionEnv : stageEnv

  return {
    env,
    productionBrowserSourceMaps: true,
    webpack: (baseConfig) => {
      const config = { ...baseConfig }
      config.resolveLoader.modules.push(path.resolve(__dirname, 'loaders'))
      config.module.rules.push({
        test: /\.md$/,
        use: ['raw-loader', 'template-literal-loader']
      })
      return config
    },
    skipTrailingSlashRedirect: true,
  }
}
