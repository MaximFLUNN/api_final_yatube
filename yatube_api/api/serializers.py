from rest_framework import serializers
from posts.models import Post, Group, Comment, Follow
from django.contrib.auth import get_user_model

User = get_user_model()


class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Post
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    following = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username'
    )

    class Meta:
        model = Follow
        fields = ('user', 'following')

    def validate_following(self, value):
        request_user = self.context['request'].user
        if request_user == value:
            raise serializers.ValidationError(
                'Невозможно подписаться на собственный аккаунт.'
            )
        return value

    def validate(self, data):
        current_user = self.context['request'].user
        target_author = data['following']
        
        if Follow.objects.filter(
                user=current_user, following=target_author).exists():
            raise serializers.ValidationError(
                'Подписка на данного автора уже существует.'
            )
        return data
