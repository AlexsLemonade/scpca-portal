import "../styles/globals.css";
import * as Sentry from "@sentry/react";
import Error from "./_error";

const Fallback = (sentry) => {
  return <Error sentry={sentry} />;
};

const Portal = ({ Component, pageProps }) => {
  // configuring sentry
  Sentry.init({
    dsn: process.env.SENTRY_DSN,
    environment: process.env.SENTRY_ENV,
  });

  return (
    <Sentry.ErrorBoundary fallback={Fallback} showDialog>
      <Component {...pageProps} />
    </Sentry.ErrorBoundary>
  );
};

export default Portal;
