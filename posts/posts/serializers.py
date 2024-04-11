# serializers.py : 장고 모델 데이터를 json 타입으로 바꿔주는 작업
# https://codemonkyu.tistory.com/entry/Djnago-Django-rest-framework-%ED%99%9C%EC%9A%A9%ED%95%98%EC%97%AC-API-%EC%84%9C%EB%B2%84-%EB%A7%8C%EB%93%A4%EA%B8%B0


# 24.04.04 base.html 확인을 위해 미작성
# -> 작성 필요


from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Post, Like, Favorite, Comment, Tag, PhotoTag


User = get_user_model()


class PostSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    likes = LikeSerializer(many=True, read_only=True)
    favorites = FavoriteSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True)
    photo_tags = PhotoTagSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            'id', 
            'user', 
            'face_chat', 
            'image_url', 
            'content', 
            'likes', 
            'favorites', 
            'comments', 
            'photo_tags', 
            'count', 
            'created_at', 
            'updated_at')

    def create(self, validated_data):
        post = post.objects.create(**validated_data)
        return post

    def update(self, instance, validated_data):
        instance.face_chat_id = validated_data.get('face_chat_id', instance.face_chat_id)
        instance.image_url = validated_data.get('image_url', instance.image_url)
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = (
            'id', 
            'author', 
            'photo', 
        )

    def create(self, validated_data):
        user = self.context['request'].user
        post = validated_data['post']
        like, created = Like.objects.get_or_create(user=user, post=post)
        if not created:
            raise serializers.ValidationError("이미 좋아요를 누른 게시글입니다.")
        post.count += 1
        post.save()
        return like

    def delete(self, instance):
        user = self.context['request'].user
        if instance.user != user:
            raise serializers.ValidationError("자신이 좋아요한 게시글만 취소할 수 있습니다.")
        post = instance.post
        post.count -= 1
        post.save()
        instance.delete()
        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = (
            'id', 
            'author', 
            'photo', 
            )

     def create(self, validated_data):
        user = self.context['request'].user
        post = validated_data['post']
        favorite, created = Favorite.objects.get_or_create(user=user, post=post)
        if not created:
            raise serializers.ValidationError("이미 즐겨찾기한 게시글입니다.")
        return favorite

    def delete(self, instance):
        user = self.context['request'].user
        if instance.user != user:
            raise serializers.ValidationError("자신이 즐겨찾기한 게시글만 해제할 수 있습니다.")
        instance.delete()
        return instance


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    replies = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = (
            'id', 
            'author', 
            'content', 
            'created_at', 
            'updated_at', 
            'parent_id',
            'photo'
            )

    def get_replies(self, obj):
        replies = Comment.objects.filter(parent_id=obj)
        return CommentSerializer(replies, many=True).data

    def validate_content(self, value):
        if len(value) < 1:
            raise serializers.ValidationError("댓글 내용을 입력해주세요.")
        return value
    
    def create(self, validated_data):
        request = self.context.get('request')
        photo_id = self.context.get('photo_id')
        photo = Photo.objects.get(id=photo_id)

        if request and request.user.is_authenticated:
            comment = Comment.objects.create(
                user_id=request.user,
                photo_id=photo,
                content=validated_data['content'],
                parent_id=validated_data.get('parent_id', None)
            )
            return comment
        else:
            raise serializers.ValidationError("로그인이 필요합니다.")

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request and request.user != instance.user_id:
            raise serializers.ValidationError('댓글 수정 권한이 없습니다.')
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance

    def delete(self, instance):
        request = self.context.get('request')
        if request and request.user != instance.user_id:
            raise serializers.ValidationError('댓글 삭제 권한이 없습니다.')
        instance.delete()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')

def create(self, validated_data):
        tag, created = Tag.objects.get_or_create(**validated_data)
        if not created:
            raise serializers.ValidationError("이미 존재하는 태그입니다.")
        return tag

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance

    def delete(self, instance):
        instance.delete()
        return instance


class PhotoTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoTag
        fields = ('id', 'photo', 'tag')

        def create(self, validated_data):
        phototag, created = PhotoTag.objects.get_or_create(**validated_data)
        if not created:
            raise serializers.ValidationError("이미 존재하는 태그입니다.")
        return PhotoTag

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance

    def delete(self, instance):
        instance.delete()
        return instance