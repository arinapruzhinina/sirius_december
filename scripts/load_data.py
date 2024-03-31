import json
import asyncio
import argparse
from datetime import datetime
from pathlib import Path
from typing import List

from sqlalchemy import insert

from webapp.db.postgres import async_session
from webapp.models.meta import metadata

parser = argparse.ArgumentParser()

parser.add_argument('fixtures', nargs='+', help='<Required> Set flag')

args = parser.parse_args()


async def main(fixtures: List[str]) -> None:
    for fixture in fixtures:
        fixture_path = Path(fixture)
        model = metadata.tables[fixture_path.stem]

        with open(fixture_path, 'r') as file:
            values = json.load(file)
        if model.name == 'reservation':
            for item in values:
                item['date_reserv'] = datetime.fromisoformat(item['date_reserv'])

        async with async_session() as session:
            await session.execute(insert(model).values(values))
            await session.commit()


if __name__ == '__main__':
    asyncio.run(main(args.fixtures))
