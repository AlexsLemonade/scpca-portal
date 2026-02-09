#!/bin/bash

set -e

TIMEOUT=120 # 2 minutes
INTERVAL=2

if [ -z "$CLIENT_DEPS_LOCKFILE" ]; then
  echo "wait_for_client: CLIENT_DEPS_LOCKFILE envar not set. Aborting."
  exit 1
fi

start_time=$(date +%s)

while [ -f "$CLIENT_DEPS_LOCKFILE" ]; do
  now=$(date +%s)
  elapsed=$(( now - start_time ))

  if [ "$elapsed" -ge "$TIMEOUT" ]; then
    echo "wait_for_client: Script timed out. Aborting."
    exit 1
  fi

  sleep "$INTERVAL"
done
