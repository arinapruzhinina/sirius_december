from conf.config import settings


def get_file_resize_cache(task_id: str) -> str:
    return f'{settings.REDIS_SIRIUS_CACHE_PREFIX}:file_resize:{task_id}'


def get_dishes_cache(category: str = None):
    if category is not None:
        return f'{settings.REDIS_SIRIUS_CACHE_PREFIX}:dishes:{category}'
    return f'{settings.REDIS_SIRIUS_CACHE_PREFIX}:dishes'


def get_dish_by_id_cache(dish_id: int):
    return f'{settings.REDIS_SIRIUS_CACHE_PREFIX}:dish:{dish_id}'


def get_restaurants_cache():
    return f'{settings.REDIS_SIRIUS_CACHE_PREFIX}:restaurants'


def get_restaurant_by_id_cache(restaurant_id: int):
    return f'{settings.REDIS_SIRIUS_CACHE_PREFIX}:restaurant:{restaurant_id}'


def get_restaurant_menu_by_id_cache(restaurant_id: int, category: str = None):
    if category is not None:
        return f'{settings.REDIS_SIRIUS_CACHE_PREFIX}:restaurant:{restaurant_id}:menu:{category}'
    return f'{settings.REDIS_SIRIUS_CACHE_PREFIX}:restaurant:{restaurant_id}:menu'


def get_reservations_cache(restaurant_id: int):
    return f'{settings.REDIS_SIRIUS_CACHE_PREFIX}:reservations:{restaurant_id}'


def get_reservation_by_id_cache(reservation_id: int):
    return f'{settings.REDIS_SIRIUS_CACHE_PREFIX}:reservation:{reservation_id}'


def get_user_by_id_cache(user_id: int):
    return f'{settings.REDIS_SIRIUS_CACHE_PREFIX}:user:{user_id}'


def get_user_reservations_by_id_cache(user_id: int):
    return f'{settings.REDIS_SIRIUS_CACHE_PREFIX}:user:{user_id}:reservations'
