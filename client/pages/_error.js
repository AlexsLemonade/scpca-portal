import React from "react";
import { useRouter } from "next/router";

const ErrorPage = ({ sentry = {} }) => {
  const router = useRouter();

  const { eventId } = sentry;

  React.useEffect(() => {
    const forceRefresh = (url) => {
      window.location = url;
    };

    router.events.on("routeChangeStart", forceRefresh);
  });

  const goBack = () => {
    router.back();
  };

  return "An error has occurred";
};

export default ErrorPage;
