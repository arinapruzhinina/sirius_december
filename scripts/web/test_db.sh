#!/usr/bin/env bash

echo "Load test data in DB"

# migrate database
python scripts/migrate.py

# load fixtures
python scripts/load_data.py fixture/sirius/sirius.user.json
python scripts/load_data.py fixture/sirius/sirius.restaurant.json
python scripts/load_data.py fixture/sirius/sirius.dish.json
python scripts/load_data.py fixture/sirius/sirius.reservation.json

