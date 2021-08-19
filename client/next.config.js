module.exports = () => {
  const isProduction = process.env.VERCEL_GIT_COMMIT_REF === 'master'

  const productionEnv = {
    SENTRY_DSN: process.env.SENTRY_DSN,
    SENTRY_ENV: process.env.SENTRY_ENV
  }

  const stageEnv = {
    SENTRY_DSN: process.env.STAGE_SENTRY_DSN,
    SENTRY_ENV: process.env.STAGE_SENTRY_ENV
  }

  const env = isProduction ? productionEnv : stageEnv

  return {
    env
  }
}
