from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from reviews.validators import validate_year


class Title(models.Model):
    name = models.CharField(verbose_name="Ttitle name", max_length=256)
    description = models.TextField(verbose_name="Title description")
    year = models.PositiveSmallIntegerField(
        verbose_name="Title year", validators=[validate_year]
    )
    category = models.ForeignKey(
        "Category",
        on_delete=models.SET_NULL,
        verbose_name="Title category",
        related_name="titles",
        null=True,
    )
    genre = models.ManyToManyField(
        "Genre",
        through="TitleGenre",
        related_name="titles",
        verbose_name="Title genres",
    )

    def __str__(self):
        return self.name


class TitleGenre(models.Model):
    genre = models.ForeignKey(
        "Genre", on_delete=models.CASCADE, verbose_name="Title genre"
    )
    title = models.ForeignKey(
        "Title", on_delete=models.CASCADE, verbose_name="Title"
    )

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ("genre", "title")


class Genre(models.Model):
    name = models.CharField(verbose_name="Genre name", max_length=256)
    slug = models.SlugField(
        verbose_name="Genre slugname", unique=True, max_length=50
    )

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(verbose_name="Category name", max_length=256)
    slug = models.SlugField(
        verbose_name="Category slugname", unique=True, max_length=50
    )

    def __str__(self):
        return self.name


class Review(models.Model):
    """Отзывы на произведения."""

    title = models.ForeignKey(
        "Title",
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Title review",
        help_text="Отзывы на произведения.",
    )
    text = models.TextField(verbose_name="Review text")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Review author",
        related_name="reviews",
        help_text="Автор отзыва.",
    )
    score = models.PositiveSmallIntegerField(
        verbose_name="Title score",
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    pub_date = models.DateTimeField(
        verbose_name="Publication date", auto_now_add=True, db_index=True
    )

    def __str__(self):
        return self.text[:15]

    class Meta:
        unique_together = ("title", "author")


class Comment(models.Model):
    """Отзывы на произведения."""

    reviews = models.ForeignKey(
        "Review",
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Review comments",
        help_text="Комментарии к отзывам.",
    )
    text = models.TextField(
        verbose_name="Comment text",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Comments author",
        related_name="comments",
        help_text="Автор отзыва.",
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата написания комментария",
        auto_now_add=True,
        db_index=True,
    )

    def __str__(self):
        return self.text[:15]
