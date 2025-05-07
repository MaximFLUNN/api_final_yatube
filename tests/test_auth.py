from http import HTTPStatus


class TestAuthAPI:

    def test_auth(self, client, user, password):
        auth_endpoint = '/api/v1/api-token-auth/'
        credentials = {'username': user.username, 'password': password}
        
        response = client.post(auth_endpoint, data=credentials)
        
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт "{auth_endpoint}" не найден. Проверьте настройки '
            'маршрутизации в файле *urls.py*.'
        )
        assert response.status_code == HTTPStatus.OK, (
            f'POST-запрос к "{auth_endpoint}" должен возвращать '
            'статус 200 при успешной аутентификации.'
        )

        response_data = response.json()
        assert 'token' in response_data, (
            f'Ответ на POST-запрос к "{auth_endpoint}" с корректными '
            'учетными данными должен содержать токен аутентификации.'
        )

    def test_auth_with_invalid_data(self, client, user):
        auth_endpoint = '/api/v1/api-token-auth/'
        
        response = client.post(auth_endpoint, data={})
        
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'POST-запрос к "{auth_endpoint}" с некорректными данными '
            'должен возвращать статус 400.'
        )
