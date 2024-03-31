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
            'user',
            'qwerty',
            1,
            status.HTTP_403_FORBIDDEN,
            [
                FIXTURES_PATH / 'sirius.user.json',
                FIXTURES_PATH / 'sirius.restaurant.json',
                FIXTURES_PATH / 'sirius.reservation.json',
            ],
        ),
        (
            'staff',
            'qwerty',
            1,
            status.HTTP_204_NO_CONTENT,
            [
                FIXTURES_PATH / 'sirius.user.json',
                FIXTURES_PATH / 'sirius.restaurant.json',
                FIXTURES_PATH / 'sirius.reservation.json',
            ],
        ),
    ],
)
@pytest.mark.asyncio()
@pytest.mark.usefixtures('_common_api_fixture')
async def test_update_reservation(
    client: AsyncClient,
    username: str,
    password: str,
    id: int,
    expected_status: int,
    access_token: str,
) -> None:
    response = await client.delete(
        URLS['reservation']['get_put_delete'].format(reservation_id=id),
        headers={'Authorization': f'Bearer Bearer {access_token}'},
    )

    assert response.status_code == expected_status
