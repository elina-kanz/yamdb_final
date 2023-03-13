from api.filters import IsOwnerFilterBackend
from api.permissions import (IsAdmin, IsAdminOrReadOnly, IsOwnerOrReadOnly,
                             IsSelf)
from api.serializers import (CategorySerializer, CommentsSerializer,
                             GenreSerializer, ReviewsSerializer,
                             TitleSerializer, UserSerializer, UsersSerializer,
                             UserTokenSerializer)
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters import rest_framework
from rest_framework import exceptions, filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Genre, Title
from users.models import User


class ListCreateViewSet(
    ListModelMixin,
    CreateModelMixin,
    viewsets.GenericViewSet,
    DestroyModelMixin,
):
    pass


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [IsOwnerFilterBackend]
    filterset_fields = (
        "genre",
        "category",
        "year",
        "name",
    )

    def perform_update(self, serializer):
        category = self.request.data.get("category")
        category_obj = get_object_or_404(Category, slug=category)
        serializer.save(category=category_obj)


class CategoryViewSet(ListCreateViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [
        rest_framework.DjangoFilterBackend,
        filters.SearchFilter,
    ]
    search_fields = ("name",)

    def destroy(self, request, *args, **kwargs):
        instance = get_object_or_404(Category, slug=kwargs["pk"])
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GenreViewSet(ListCreateViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [
        rest_framework.DjangoFilterBackend,
        filters.SearchFilter,
    ]
    search_fields = ("name",)

    def destroy(self, request, *args, **kwargs):
        instance = get_object_or_404(Genre, slug=kwargs["pk"])
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReviewsViewSet(viewsets.ModelViewSet):
    """Класс представление модели Review."""

    permission_classes = [IsOwnerOrReadOnly]
    serializer_class = ReviewsSerializer

    def get_queryset(self):
        title_id = self.kwargs.get("title_id")
        title_obj = get_object_or_404(Title, id=title_id)
        return title_obj.reviews.all()

    def perform_create(self, serializer):
        title_obj = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        serializer.save(title=title_obj, author=self.request.user)


class CommentsViewSet(viewsets.ModelViewSet):
    """Класс представление модели Comment."""

    permission_classes = [IsOwnerOrReadOnly]
    serializer_class = CommentsSerializer

    def get_queryset(self):
        title_obj = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        reviews_obj = title_obj.reviews.all()
        review_obj = get_object_or_404(
            reviews_obj, id=self.kwargs.get("review_id")
        )
        return review_obj.comments.all()

    def perform_create(self, serializer):
        title_obj = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        reviews_obj = title_obj.reviews.all()
        review_obj = get_object_or_404(
            reviews_obj, id=self.kwargs.get("review_id")
        )
        serializer.save(reviews=review_obj, author=self.request.user)


class RegistrationAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response_data = {
            "username": request.data.get("username"),
            "email": request.data.get("email"),
        }
        if User.objects.filter(username=request.data.get("username")).exists():
            user_obj = User.objects.get(username=request.data.get("username"))
            if user_obj.email != request.data.get("email"):
                raise exceptions.ParseError
            send_mail(
                "confirmation code",
                user_obj.confirmation_code,
                settings.DEFAULT_MAIL,
                [user_obj.email],
            )
            return Response(response_data, status=status.HTTP_200_OK)
        serializer.is_valid(raise_exception=True)
        user_obj = serializer.save()
        send_mail(
            "confirmation_code",
            user_obj.confirmation_code,
            settings.DEFAULT_MAIL,
            [request.data.get("email")],
        )
        return Response(response_data, status=status.HTTP_200_OK)


class UsersModelViewSet(viewsets.ModelViewSet):
    serializer_class = UsersSerializer
    permission_classes = [IsAdmin]
    http_method_names = ["get", "post", "head", "patch", "delete"]
    lookup_field = "username"
    filter_backends = [filters.SearchFilter]
    search_fields = ["username"]

    def get_queryset(self):
        user_obj = self.kwargs.get("username")
        if user_obj:
            return User.objects.filter(username=user_obj)
        return User.objects.all()

    def retrieve(self, request, username=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def partial_update(self, request, username=None):
        user = get_object_or_404(User, username=username)
        serializer = UsersSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=["get", "patch"], permission_classes=[IsSelf]
    )
    def me(self, request):
        serializer = UsersSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role)
        return Response(serializer.data)


class UserTokenView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = UserTokenSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get("username")
            confirmation_code = serializer.validated_data.get(
                "confirmation_code"
            )
            user = get_object_or_404(User, username=username)
            if default_token_generator.check_token(user, confirmation_code):
                token = AccessToken.for_user(user)
                return Response(
                    {"token": f"{token}"}, status=status.HTTP_200_OK
                )
            return Response(
                {"confirmation_code": "Неверный код подтверждения"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
