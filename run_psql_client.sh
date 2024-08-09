#! /bin/sh
docker compose --env-file ./docker-compose.env run --rm postgres psql -h postgres -U postgres -d postgres
