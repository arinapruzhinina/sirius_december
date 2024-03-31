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
        'expected_status',
        'fixtures',
    ),
    [
        (
            'admin',
            'qwerty',
            1,
            status.HTTP_204_NO_CONTENT,
            [
                FIXTURES_PATH / 'sirius.user.json',
                FIXTURES_PATH / 'sirius.restaurant.json',
            ],
        ),
        (
            'user',
            'qwerty',
            1,
            status.HTTP_403_FORBIDDEN,
            [
                FIXTURES_PATH / 'sirius.user.json',
                FIXTURES_PATH / 'sirius.restaurant.json',
            ],
        ),
    ],
)
@pytest.mark.asyncio()
@pytest.mark.usefixtures('_common_api_fixture')
async def test_delete_restaurant(
    client: AsyncClient,
    username: str,
    password: str,
    id: int,
    expected_status: int,
    access_token: str,
) -> None:
    response = await client.delete(
        URLS['restaurant']['get_put_delete'].format(restaurant_id=id),
        headers={'Authorization': f'Bearer Bearer {access_token}'},
    )

    assert response.status_code == expected_status
