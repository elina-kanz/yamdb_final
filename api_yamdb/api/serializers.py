from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from reviews.models import Category, Comment, Genre, Review, Title, TitleGenre
from users.models import User

ROLE_CHOICES = [
    (User.USER, User.USER),
    (User.MODERATOR, User.MODERATOR),
    (User.ADMIN, User.ADMIN),
]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug")
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug")
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        fields = "__all__"
        model = Title

    def get_rating(self, instance):
        return instance.reviews.aggregate(Avg("score"))["score__avg"]

    def create(self, validated_data):
        genres = self.initial_data.getlist("genre")
        categoryes = self.initial_data.get("category")
        category = get_object_or_404(Category, slug=categoryes)
        title = Title.objects.create(**validated_data, category=category)
        for genre in genres:
            current_genre = get_object_or_404(Genre, slug=genre)
            TitleGenre.objects.create(genre=current_genre, title=title)
        return title


class ReviewsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field="username"
    )

    class Meta:
        fields = ("id", "text", "author", "score", "pub_date")
        model = Review

    def validate(self, data):
        user_obj = self.context["request"].user
        my_view = self.context["view"]
        title_id = my_view.kwargs.get("title_id")
        pk_id = my_view.kwargs.get("pk")
        if pk_id:
            return data
        if Review.objects.filter(title=title_id, author=user_obj).exists():
            raise serializers.ValidationError(
                "Вы уже писали отзыв к этому произведению."
            )
        return data


class CommentsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field="username"
    )

    class Meta:
        fields = ("id", "text", "author", "pub_date")
        model = Comment


class UserSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=255, read_only=True)
    password = serializers.CharField(required=False, read_only=True)
    role = serializers.CharField(default="user")
    username = serializers.RegexField(
        "^[\\w.@+-]+", max_length=150, required=True
    )
    first_name = serializers.CharField(required=False, max_length=150)
    last_name = serializers.CharField(required=False, max_length=150)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "bio",
            "role",
            "token",
            "first_name",
            "last_name",
        )

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def validate_username(self, username):
        if username.lower() == "me":
            raise serializers.ValidationError(
                "Нельзя использовать `me` как имя!"
            )
        return username


class UsersSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=255, read_only=True)
    role = serializers.ChoiceField(choices=ROLE_CHOICES, default="user")
    username = serializers.RegexField(
        "^[\\w.@+-]+", max_length=150, required=True
    )
    first_name = serializers.CharField(required=False, max_length=150)
    last_name = serializers.CharField(required=False, max_length=150)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "bio",
            "role",
            "token",
            "first_name",
            "last_name",
        )

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def validate_username(self, username):
        if username.lower() == "me":
            raise serializers.ValidationError(
                "Нельзя использовать `me` как имя!"
            )
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                "Пользователь с таким именем уже существует"
            )
        return username


class UserTokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, max_length=150)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ("username", "confirmation_code")
