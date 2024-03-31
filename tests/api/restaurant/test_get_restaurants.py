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
        'list_len',
        'expected_status',
        'fixtures',
    ),
    [
        (
            2,
            'Ресторан В',
            'пр. Дубовый, 456',
            'Современный ресторан с фьюжн-кухней',
            2,
            status.HTTP_200_OK,
            [
                FIXTURES_PATH / 'sirius.restaurant.json',
            ],
        ),
    ],
)
@pytest.mark.asyncio()
@pytest.mark.usefixtures('_common_api_fixture')
async def test_get_restaurants(
    client: AsyncClient,
    id: int,
    name: str,
    address: str,
    description: str,
    list_len: int,
    expected_status: int,
) -> None:
    response = await client.get(
        URLS['restaurant']['get_all_create'],
    )

    assert response.status_code == expected_status
    response_data = response.json()
    assert len(response_data) == list_len
    assert response_data[1]['id'] == id
    assert response_data[1]['name'] == name
    assert response_data[1]['address'] == address
    assert response_data[1]['description'] == description
