import pytest
from httpx import AsyncClient
from starlette import status

from tests.const import URLS


@pytest.mark.parametrize(
    ('username', 'password', 'phone', 'role', 'user_id', 'expected_status', 'fixtures'),
    [
        (
            'test_user',
            'qwerty',
            '+79991234567',
            'Пользователь',
            1,
            status.HTTP_201_CREATED,
            [],
        ),
    ],
)
@pytest.mark.asyncio()
@pytest.mark.usefixtures('_common_api_fixture')
async def test_signup(
    client: AsyncClient,
    username: str,
    password: str,
    phone: str,
    role: str,
    user_id: int,
    expected_status: int,
    db_session: None,
) -> None:
    response = await client.post(
        URLS['auth']['signup'], json={'username': username, 'password': password, 'phone': phone}
    )

    assert response.status_code == expected_status
    response_data = response.json()
    assert response_data['username'] == username
    assert response_data['phone'] == phone
    assert response_data['role'] == role
    assert response_data['id'] == user_id
