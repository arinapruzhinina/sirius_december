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
        'phone',
        'id',
        'role',
        'expected_status',
        'fixtures',
    ),
    [
        (
            'user',
            'qwerty',
            '+79991234567',
            1,
            'Пользователь',
            status.HTTP_200_OK,
            [
                FIXTURES_PATH / 'sirius.user.json',
            ],
        ),
    ],
)
@pytest.mark.asyncio()
@pytest.mark.usefixtures('_common_api_fixture')
async def test_get_me(
    client: AsyncClient,
    username: str,
    password: str,
    phone: str,
    id: int,
    role: str,
    expected_status: int,
    access_token: str,
) -> None:
    response = await client.get(
        URLS['user']['me'],
        headers={'Authorization': f'Bearer Bearer {access_token}'},
    )

    assert response.status_code == expected_status
    response_data = response.json()
    assert response_data['username'] == username
    assert response_data['phone'] == phone
    assert response_data['id'] == id
    assert response_data['role'] == role
