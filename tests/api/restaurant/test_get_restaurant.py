from pathlib import Path

import pytest
from httpx import AsyncClient
from starlette import status

from tests.const import URLS

BASE_DIR = Path(__file__).parent
FIXTURES_PATH = BASE_DIR / 'fixtures'


@pytest.mark.parametrize(
    (
        'id',
        'name',
        'address',
        'description',
        'expected_status',
        'fixtures',
    ),
    [
        (
            2,
            'Ресторан В',
            'пр. Дубовый, 456',
            'Современный ресторан с фьюжн-кухней',
            status.HTTP_200_OK,
            [
                FIXTURES_PATH / 'sirius.restaurant.json',
            ],
        ),
    ],
)
@pytest.mark.asyncio()
@pytest.mark.usefixtures('_common_api_fixture')
async def test_get_restaurant(
    client: AsyncClient,
    id: int,
    name: str,
    address: str,
    description: str,
    expected_status: int,
) -> None:
    response = await client.get(
        URLS['restaurant']['get_put_delete'].format(restaurant_id=id),
    )

    assert response.status_code == expected_status
    response_data = response.json()
    assert response_data['id'] == id
    assert response_data['name'] == name
    assert response_data['address'] == address
    assert response_data['description'] == description
