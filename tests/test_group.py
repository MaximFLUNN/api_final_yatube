from http import HTTPStatus

import pytest

from posts.models import Group, Post


class TestGroupAPI:

    @pytest.mark.django_db(transaction=True)
    def test_group_not_found(self, client, group_1):
        groups_endpoint = '/api/v1/groups/'
        response = client.get(groups_endpoint)

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт "{groups_endpoint}" не обнаружен. Проверьте '
            'настройки маршрутизации в файле *urls.py*.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_group_not_auth(self, client, group_1):
        groups_endpoint = '/api/v1/groups/'
        response = client.get(groups_endpoint)
        
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            f'GET-запрос неавторизованного пользователя к "{groups_endpoint}" '
            'должен возвращать статус 401.'
        )

    def verify_group_fields(self, group_data, endpoint_url):
        required_fields = ['id', 'title', 'slug', 'description']
        
        for field in required_fields:
            assert field in group_data, (
                f'Ответ на GET-запрос к "{endpoint_url}" не содержит '
                f'обязательное поле "{field}". Проверьте настройки '
                'сериализатора модели Group.'
            )

    @pytest.mark.django_db(transaction=True)
    def test_group_auth_get(self, user_client, group_1, group_2):
        groups_endpoint = '/api/v1/groups/'
        response = user_client.get(groups_endpoint)
        
        assert response.status_code == HTTPStatus.OK, (
            f'GET-запрос авторизованного пользователя к "{groups_endpoint}" '
            'должен возвращать статус 200.'
        )

        response_data = response.json()
        assert isinstance(response_data, list), (
            f'GET-запрос авторизованного пользователя к "{groups_endpoint}" '
            'должен возвращать список групп.'
        )
        assert len(response_data) == Group.objects.count(), (
            f'GET-запрос авторизованного пользователя к "{groups_endpoint}" '
            'должен возвращать все существующие группы.'
        )

        test_group = response_data[0]
        self.verify_group_fields(test_group, groups_endpoint)

    @pytest.mark.django_db(transaction=True)
    def test_group_create(self, user_client, group_1, group_2):
        groups_endpoint = '/api/v1/groups/'
        new_group_data = {'title': 'Новая тестовая группа'}
        
        response = user_client.post(groups_endpoint, data=new_group_data)
        
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            'Создание групп должно быть доступно только через админ-панель. '
            f'POST-запрос к "{groups_endpoint}" должен возвращать статус 405.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_group_get_post(self, user_client, post_2):
        posts_endpoint = '/api/v1/posts/'
        response = user_client.get(posts_endpoint)
        
        assert response.status_code == HTTPStatus.OK, (
            f'Эндпоинт "{posts_endpoint}" не найден. Проверьте настройки '
            'маршрутизации в файле *urls.py*.'
        )

        response_data = response.json()
        assert len(response_data) == Post.objects.count(), (
            f'GET-запрос к "{posts_endpoint}" должен возвращать все посты, '
            'включая посты, принадлежащие группам.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_group_page_not_found(self, client, group_1):
        group_detail_endpoint = f'/api/v1/groups/{group_1.id}/'
        response = client.get(group_detail_endpoint)
        
        assert response.status_code != 404, (
            f'Эндпоинт "{group_detail_endpoint}" не найден. Проверьте '
            'настройки маршрутизации в файле *urls.py*.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_group_page_not_auth(self, client, group_1):
        group_detail_endpoint = f'/api/v1/groups/{group_1.id}/'
        response = client.get(group_detail_endpoint)
        
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            f'GET-запрос неавторизованного пользователя к "{group_detail_endpoint}" '
            'должен возвращать статус 401.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_group_page_auth_get(self, user_client, group_1):
        group_detail_endpoint = f'/api/v1/groups/{group_1.id}/'
        response = user_client.get(group_detail_endpoint)
        
        assert response.status_code == HTTPStatus.OK, (
            f'GET-запрос авторизованного пользователя к "{group_detail_endpoint}" '
            'должен возвращать статус 200.'
        )

        response_data = response.json()
        assert isinstance(response_data, dict), (
            f'GET-запрос авторизованного пользователя к "{group_detail_endpoint}" '
            'должен возвращать информацию о группе в виде словаря.'
        )
        self.verify_group_fields(response_data, group_detail_endpoint)
