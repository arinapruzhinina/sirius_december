from pathlib import Path

import pytest
from dateutil.parser import parse
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
        'new_restaurant_id',
        'new_date_reserv',
        'new_guest_count',
        'new_comment',
        'new_responce_status',
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
            '2024-03-14T13:30:00.390Z',
            4,
            'Столик около окна в зоне кальяна',
            True,
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
            1,
            1,
            '2024-03-14T13:30:00.390Z',
            4,
            'Столик около окна в зоне кальяна',
            True,
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
async def test_update_reservation(
    client: AsyncClient,
    username: str,
    password: str,
    id: int,
    user_id: int,
    new_restaurant_id: int,
    new_date_reserv: str,
    new_guest_count: int,
    new_comment: str,
    new_responce_status: bool,
    expected_status: int,
    access_token: str,
) -> None:
    response = await client.put(
        URLS['reservation']['get_put_delete'].format(reservation_id=id),
        headers={'Authorization': f'Bearer Bearer {access_token}'},
        json={
            'user_id': user_id,
            'restaurant_id': new_restaurant_id,
            'date_reserv': new_date_reserv,
            'guest_count': new_guest_count,
            'comment': new_comment,
            'status': new_responce_status,
        },
    )

    assert response.status_code == expected_status
    if response.status_code == status.HTTP_201_CREATED:
        response_data = response.json()
        assert response_data['id'] == id
        assert response_data['user_id'] == user_id
        assert response_data['restaurant_id'] == new_restaurant_id
        assert parse(response_data['date_reserv']) == parse(new_date_reserv)
        assert response_data['guest_count'] == new_guest_count
        assert response_data['comment'] == new_comment
        assert response_data['status'] == new_responce_status
