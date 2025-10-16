#!/usr/bin/env sh
set -e

python manage.py migrate --no-input

if [ -f "fixtures/mock_restaurants.json" ]; then
    python manage.py loaddata fixtures/mock_restaurants.json
fi

if [ -f "fixtures/mock_offers.json" ]; then
    python manage.py loaddata fixtures/mock_offers.json
fi

python manage.py collectstatic --no-input

exec "$@"
