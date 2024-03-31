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
        'category',
        'restaurant_id',
        'dish_name',
        'description',
        'price',
        'expected_status',
        'fixtures',
    ),
    [
        (
            'staff',
            'qwerty',
            1,
            'Основное блюдо',
            1,
            'Паста с лососем',
            'Феттучини с копчёным лососем в соусе из сливок и укропа',
            4.89,
            status.HTTP_201_CREATED,
            [
                FIXTURES_PATH / 'sirius.user.json',
                FIXTURES_PATH / 'sirius.restaurant.json',
            ],
        ),
        (
            'user',
            'qwerty',
            1,
            'Основное блюдо',
            1,
            'Паста с лососем',
            'Феттучини с копчёным лососем в соусе из сливок и укропа',
            4.89,
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
async def test_create_dish(
    client: AsyncClient,
    username: str,
    password: str,
    id: int,
    category: str,
    restaurant_id: int,
    dish_name: str,
    description: str,
    price: float,
    expected_status: int,
    access_token: str,
) -> None:
    response = await client.post(
        URLS['dish']['get_all_create'],
        headers={'Authorization': f'Bearer Bearer {access_token}'},
        json={
            'category': category,
            'restaurant_id': restaurant_id,
            'dish_name': dish_name,
            'description': description,
            'price': price,
        },
    )

    assert response.status_code == expected_status
    if response.status_code == status.HTTP_201_CREATED:
        response_data = response.json()
        assert response_data['id'] == id
        assert response_data['category'] == category
        assert response_data['restaurant_id'] == restaurant_id
        assert response_data['dish_name'] == dish_name
        assert response_data['description'] == description
        assert response_data['price'] == price
