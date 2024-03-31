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
        'new_category',
        'new_restaurant_id',
        'new_dish_name',
        'new_description',
        'new_price',
        'expected_status',
        'fixtures',
    ),
    [
        (
            'staff',
            'qwerty',
            2,
            'Закуска',
            2,
            'Брускетта с авокадо и лососем',
            'Чесночная брускетта с авокадо и лососем приправленная итальянскими травами и соком лимона',
            7.89,
            status.HTTP_200_OK,
            [
                FIXTURES_PATH / 'sirius.user.json',
                FIXTURES_PATH / 'sirius.restaurant.json',
                FIXTURES_PATH / 'sirius.dish.json',
            ],
        ),
        (
            'user',
            'qwerty',
            2,
            'Закуска',
            2,
            'Брускетта с авокадо и лососем',
            'Чесночная брускетта с авокадо и лососем приправленная итальянскими травами и соком лимона',
            7.89,
            status.HTTP_403_FORBIDDEN,
            [
                FIXTURES_PATH / 'sirius.user.json',
                FIXTURES_PATH / 'sirius.restaurant.json',
                FIXTURES_PATH / 'sirius.dish.json',
            ],
        ),
    ],
)
@pytest.mark.asyncio()
@pytest.mark.usefixtures('_common_api_fixture')
async def test_update_dish(
    client: AsyncClient,
    username: str,
    password: str,
    id: int,
    new_category: str,
    new_restaurant_id: int,
    new_dish_name: str,
    new_description: str,
    new_price: float,
    expected_status: int,
    access_token: str,
) -> None:
    response = await client.put(
        URLS['dish']['get_put_delete'].format(dish_id=id),
        headers={'Authorization': f'Bearer Bearer {access_token}'},
        json={
            'category': new_category,
            'restaurant_id': new_restaurant_id,
            'dish_name': new_dish_name,
            'description': new_description,
            'price': new_price,
        },
    )

    assert response.status_code == expected_status
    if response.status_code == status.HTTP_200_OK:
        response_data = response.json()
        assert response_data['id'] == id
        assert response_data['category'] == new_category
        assert response_data['restaurant_id'] == new_restaurant_id
        assert response_data['dish_name'] == new_dish_name
        assert response_data['description'] == new_description
        assert response_data['price'] == new_price
