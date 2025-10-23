from django.contrib import admin
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import IngredientRecipeInlineForm
from .models import (
    Ingredient, Tag, Recipe,
    IngredientRecipe, Favorite,
    Cart, User, Subscriptions
)


class CountDisplayMixin:
    """Миксин для отображения количества рецептов."""

    @admin.display(description='Рецепты')
    def get_recipe_count(self, obj):
        return obj.recipes.count()


@admin.register(User)
class UserAdmin(BaseUserAdmin, CountDisplayMixin):
    list_display = (
        'id',
        'username',
        'full_name',
        'email',
        'avatar_display',
        'subscriptions_count',
        'subscribers_count',
        'get_recipe_count',
    )
    readonly_fields = ('avatar_display',)
    search_fields = ('username', 'email', 'first_name', 'last_name')
    save_on_top = True

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Персональная информация',
         {'fields': ('first_name', 'last_name', 'avatar', 'avatar_display')}),
    )

    @admin.display(description='Аватар')
    def avatar_display(self, user):
        if user.avatar:
            return mark_safe(
                f'<img src="{user.avatar.url}" '
                f'width="50" height="50" style="border-radius: 50%;" />'
            )
        return '-'

    @admin.display(description='ФИО')
    def full_name(self, user):
        return f'{user.first_name} {user.last_name}'.strip()

    @admin.display(description='Подписок')
    def subscriptions_count(self, user):
        return user.subscribers.count()

    @admin.display(description='Подписчиков')
    def subscribers_count(self, user):
        return user.authors.count()


@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user__username', 'author__username')
    list_filter = ('user', 'author')


class IngredientInline(admin.TabularInline):
    model = IngredientRecipe
    form = IngredientRecipeInlineForm
    extra = 2


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin, CountDisplayMixin):
    list_display = ('name', 'measurement_unit', 'get_recipe_count')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)
    ordering = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin, CountDisplayMixin):
    list_display = ('name', 'slug', 'get_recipe_count')
    search_fields = ('name', 'slug')
    list_filter = ('name',)
    ordering = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'get_cooking_time', 'author', 'get_tags',
        'get_ingredients', 'get_favorite_count', 'get_image'
    )
    search_fields = ('name', 'author__username', 'tags__name', 'tags__slug')
    list_filter = ('tags', 'author')
    ordering = ('-id',)
    inlines = (IngredientInline,)

    @admin.display(description='Теги')
    def get_tags(self, recipe):
        return mark_safe('<br>'.join(tag.name for tag in recipe.tags.all()))

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, recipe):
        ingredients = recipe.recipe_ingredients.all()
        return mark_safe('<br>'.join(
            f"{item.ingredient.name} "
            f"({item.amount} {item.ingredient.measurement_unit})"
            for item in ingredients
        ))

    @admin.display(description='В избранном')
    def get_favorite_count(self, recipe):
        return recipe.favorites.count()

    @admin.display(description='Картинка')
    def get_image(self, recipe):
        if recipe.image:
            return mark_safe(
                f'<img src="{recipe.image.url}" '
                f'width="50" height="50" style="object-fit: cover;" />'
            )
        return '-'

    @admin.display(description='Время (мин)')
    def get_cooking_time(self, recipe):
        return recipe.cooking_time


@admin.register(Favorite, Cart)
class UserRecipeRelationAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user',)
    ordering = ('user',)
