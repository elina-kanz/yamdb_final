from api.views import (CategoryViewSet, CommentsViewSet, GenreViewSet,
                       RegistrationAPIView, ReviewsViewSet, TitleViewSet,
                       UsersModelViewSet, UserTokenView)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router_v1 = DefaultRouter()
router_v1.register(r"titles", TitleViewSet)
router_v1.register(r"categories", CategoryViewSet)
router_v1.register(r"genres", GenreViewSet)
router_v1.register(
    r"titles/(?P<title_id>\d+)/reviews", ReviewsViewSet, basename="Review"
)
router_v1.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentsViewSet,
    basename="Comment",
)
router_v1.register(r"users", UsersModelViewSet, basename="User")

auth_urlpatterns = [
    path("signup/", RegistrationAPIView.as_view()),
    path("token/", UserTokenView.as_view()),
]

urlpatterns = [
    path("v1/", include(router_v1.urls)),

    path("v1/auth/", include(auth_urlpatterns)),
]
