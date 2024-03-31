URLS = {
    'auth': {
        'login': '/auth/login',
        'info': '/auth/info',
        'signup': '/auth/signup',
    },
    'dish': {
        'get_all_create': '/dishes',
        'get_by_category': '/dishes/?category={category}',
        'get_put_delete': '/dishes/{dish_id}',
    },
    'restaurant': {
        'get_all_create': '/restaurants',
        'get_put_delete': '/restaurants/{restaurant_id}',
        'get_menu': '/restaurants/{restaurant_id}/menu',
        'get_menu_by_category': '/restaurants/{restaurant_id}/menu?category={category}',
    },
    'reservation': {
        'create': '/reservations',
        '[1]': '/reservations/{restaurants_id}',
        'get_put_delete': '/reservations/{reservation_id}',
    },
    'user': {
        'me': '/users/me',
        'reservations': '/users/me/reservations',
        'update': '/users/me/update',
        'delete': '/users/me/delete',
    },
}
