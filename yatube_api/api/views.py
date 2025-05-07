from api.pagination import ConditionalPagination

from rest_framework import viewsets, mixins, filters
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.exceptions import PermissionDenied

from posts.models import Post, Group, Comment, Follow
from api.serializers import (
    PostSerializer,
    GroupSerializer,
    CommentSerializer,
    FollowSerializer
)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = ConditionalPagination  # Используем кастомный пагинатор

    def perform_create(self, serializer):
        # Автоматически устанавливаем текущего пользователя как автора
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        # Проверяем, что пользователь является автором публикации
        if serializer.instance.author != self.request.user:
            raise PermissionDenied('Редактирование чужих публикаций запрещено!')
        serializer.save()

    def perform_destroy(self, instance):
        # Проверяем, что пользователь является автором публикации
        if instance.author != self.request.user:
            raise PermissionDenied('Удаление чужих публикаций запрещено!')
        instance.delete()


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None  # Отключаем пагинацию для групп


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None  # Отключаем пагинацию для комментариев

    def get_queryset(self):
        # Получаем только комментарии для конкретного поста
        return Comment.objects.filter(post=self.kwargs['post_id'])

    def perform_create(self, serializer):
        # Создаем комментарий с автором и привязкой к посту
        serializer.save(
            author=self.request.user,
            post_id=self.kwargs['post_id']
        )

    def perform_update(self, serializer):
        # Проверяем, что пользователь является автором комментария
        if serializer.instance.author != self.request.user:
            raise PermissionDenied('Редактирование чужих комментариев запрещено!')
        serializer.save()

    def perform_destroy(self, instance):
        # Проверяем, что пользователь является автором комментария
        if instance.author != self.request.user:
            raise PermissionDenied('Удаление чужих комментариев запрещено!')
        instance.delete()


class FollowViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['following__username']
    pagination_class = None  # Отключаем пагинацию для подписок

    def get_queryset(self):
        # Получаем только подписки текущего пользователя
        return Follow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Автоматически устанавливаем текущего пользователя как подписчика
        serializer.save(user=self.request.user)
