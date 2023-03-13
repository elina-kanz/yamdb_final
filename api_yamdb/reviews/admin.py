from django.contrib import admin
from reviews.models import Category, Genre, Review, Title


class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "title",
        "text",
        "score",
        "pub_date",
    )
    search_fields = ("titles",)
    list_filter = ("pub_date",)
    list_editable = ("text",)
    empty_value_display = "-пусто-"


class TitleAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "year", "category", "genre", "rating")
    search_fields = ("name",)
    list_filter = ("year", "rating")
    list_editable = ("category",)
    empty_value_display = "-пусто-"


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "slug")


class GenreAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "slug")


admin.site.register(Title)
admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(Review)
