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
        'new_username',
        'new_phone',
        'user_id',
        'expected_status',
        'fixtures',
    ),
    [
        (
            'user',
            'qwerty',
            'my_new_username',
            '89976543454',
            1,
            status.HTTP_200_OK,
            [
                FIXTURES_PATH / 'sirius.user.json',
            ],
        ),
    ],
)
@pytest.mark.asyncio()
@pytest.mark.usefixtures('_common_api_fixture')
async def test_update_me(
    client: AsyncClient,
    username: str,
    password: str,
    new_username: str,
    new_phone: str,
    user_id: int,
    expected_status: int,
    access_token: str,
) -> None:
    response = await client.put(
        URLS['user']['update'],
        headers={'Authorization': f'Bearer Bearer {access_token}'},
        json={'username': new_username, 'phone': new_phone},
    )

    assert response.status_code == expected_status
    response_data = response.json()
    assert response_data['id'] == user_id
    assert response_data['phone'] == new_phone
    assert response_data['username'] == new_username
