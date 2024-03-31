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
        'expected_status',
        'fixtures',
    ),
    [
        (
            4,
            'Закуска',
            2,
            'Салат Капрезе',
            'Свежий моцарелла, помидоры и базилик с бальзамическим уксусом',
            8.99,
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
async def test_get_dish(
    client: AsyncClient,
    id: int,
    category: str,
    restaurant_id: int,
    dish_name: str,
    description: str,
    price: float,
    expected_status: int,
) -> None:
    response = await client.get(
        URLS['dish']['get_put_delete'].format(dish_id=id),
    )

    assert response.status_code == expected_status
    response_data = response.json()
    assert response_data['id'] == id
    assert response_data['category'] == category
    assert response_data['restaurant_id'] == restaurant_id
    assert response_data['dish_name'] == dish_name
    assert response_data['description'] == description
    assert response_data['price'] == price
