from pathlib import Path

import pytest
from httpx import AsyncClient
from starlette import status

from tests.const import URLS

BASE_DIR = Path(__file__).parent
FIXTURES_PATH = BASE_DIR / 'fixtures'


@pytest.mark.parametrize(
    (
        'username',
        'password',
        'id',
        'name',
        'address',
        'description',
        'expected_status',
        'fixtures',
    ),
    [
        (
            'admin',
            'qwerty',
            1,
            'Уютное место',
            'г. Москва, пр-кт Ленина, д. 298',
            'Самое уютное место с кухней премиум класса',
            status.HTTP_201_CREATED,
            [
                FIXTURES_PATH / 'sirius.user.json',
            ],
        ),
        (
            'user',
            'qwerty',
            1,
            'Уютное место',
            'г. Москва, пр-кт Ленина, д. 298',
            'Самое уютное место с кухней премиум класса',
            status.HTTP_403_FORBIDDEN,
            [
                FIXTURES_PATH / 'sirius.user.json',
            ],
        ),
    ],
)
@pytest.mark.asyncio()
@pytest.mark.usefixtures('_common_api_fixture')
async def test_create_restaurant(
    client: AsyncClient,
    username: str,
    password: str,
    id: int,
    name: str,
    address: int,
    description: str,
    expected_status: int,
    access_token: str,
) -> None:
    response = await client.post(
        URLS['restaurant']['get_all_create'],
        headers={'Authorization': f'Bearer Bearer {access_token}'},
        json={'name': name, 'address': address, 'description': description},
    )

    assert response.status_code == expected_status
    if response.status_code == status.HTTP_201_CREATED:
        response_data = response.json()
        assert response_data['id'] == id
        assert response_data['name'] == name
        assert response_data['address'] == address
        assert response_data['description'] == description
