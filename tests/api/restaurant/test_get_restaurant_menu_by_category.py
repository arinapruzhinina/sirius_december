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
        'category',
        'restaurant_id',
        'dish_name',
        'description',
        'price',
        'list_len',
        'expected_status',
        'fixtures',
    ),
    [
        (
            6,
            'Десерт',
            2,
            'Чизкейк',
            'Нежный чизкейк с основой из грэхемовых сухарей',
            7.99,
            1,
            status.HTTP_200_OK,
            [
                FIXTURES_PATH / 'sirius.restaurant.json',
                FIXTURES_PATH / 'sirius.dish.json',
            ],
        ),
    ],
)
@pytest.mark.asyncio()
@pytest.mark.usefixtures('_common_api_fixture')
async def test_get_restaurant_menu_by_category(
    client: AsyncClient,
    id: int,
    category: str,
    restaurant_id: int,
    dish_name: str,
    description: str,
    price: float,
    list_len: int,
    expected_status: int,
) -> None:
    response = await client.get(
        URLS['restaurant']['get_menu_by_category'].format(restaurant_id=restaurant_id, category=category),
    )

    assert response.status_code == expected_status
    response_data = response.json()
    assert len(response_data) == list_len
    assert response_data[0]['id'] == id
    assert response_data[0]['category'] == category
    assert response_data[0]['restaurant_id'] == restaurant_id
    assert response_data[0]['dish_name'] == dish_name
    assert response_data[0]['description'] == description
    assert response_data[0]['price'] == price
