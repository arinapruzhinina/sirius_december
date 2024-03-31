from datetime import datetime
from pathlib import Path
from dateutil.parser import parse
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
        'user_id',
        'restaurant_id',
        'date_reserv',
        'guest_count',
        'comment',
        'list_len',
        'expected_status',
        'fixtures',
    ),
    [
        (
            'user',
            'qwerty',
            1,
            1,
            1,
            '2024-03-03T11:30:57.390Z',
            2,
            'Особые требования к столику',
            1,
            status.HTTP_200_OK,
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
async def test_my_reservations(
    client: AsyncClient,
    username: str,
    password: str,
    id: int,
    user_id: int,
    restaurant_id: int,
    date_reserv: datetime,
    guest_count: int,
    comment: str,
    list_len: 1,
    expected_status: int,
    access_token: str,
) -> None:
    response = await client.get(
        URLS['user']['reservations'],
        headers={'Authorization': f'Bearer Bearer {access_token}'},
    )

    assert response.status_code == expected_status
    response_data = response.json()
    assert len(response_data) == list_len
    assert response_data[0]['id'] == id
    assert response_data[0]['user_id'] == user_id
    assert response_data[0]['restaurant_id'] == restaurant_id
    assert parse(response_data[0]['date_reserv']) == parse(date_reserv)
    assert response_data[0]['guest_count'] == guest_count
    assert response_data[0]['comment'] == comment
