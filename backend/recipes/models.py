"""Модуль для создания, настройки и управления моделями пакета `recipe`."""
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db.models import (
    CASCADE,
    SET_NULL,
    CharField,
    DateTimeField,
    EmailField,
    ForeignKey,
    ImageField,
    ManyToManyField,
    Model,
    PositiveSmallIntegerField,
    TextField,
    UniqueConstraint,
)
from django.db.models.functions import Length

from recipes.additional import Limits

CharField.register_lookup(Length)


class User(AbstractUser):
    """Модель пользователя"""

    email = EmailField(
        verbose_name="Адрес электронной почты",
        max_length=Limits.MAX_LEN_EMAIL_FIELD.value,
        unique=True,
    )
    username = CharField(
        verbose_name="Логин",
        max_length=Limits.MAX_LEN_USERS_CHARFIELD.value,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message="Допустимы только буквы, цифры и символы .@+-"
            )
        ],
    )
    first_name = CharField(
        verbose_name="Имя",
        max_length=Limits.MAX_LEN_USERS_CHARFIELD.value,
    )
    last_name = CharField(
        verbose_name="Фамилия",
        max_length=Limits.MAX_LEN_USERS_CHARFIELD.value,
        help_text=(
            "Обязательно для заполнения. "
            f"Максимум {Limits.MAX_LEN_USERS_CHARFIELD} букв."
        ),
    )
    avatar = ImageField(
        upload_to="avatars/",
        verbose_name="Аватар",
        blank=True,
        null=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)

    def __str__(self):
        return f"{self.username}: {self.email}"


class Subscriptions(Model):
    """Подписки пользователей."""

    author = ForeignKey(
        verbose_name="Автор",
        related_name="authors",
        to=User,
        on_delete=CASCADE,
    )
    user = ForeignKey(
        verbose_name="Подписчик",
        related_name="subscribers",
        to=User,
        on_delete=CASCADE,
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            UniqueConstraint(
                fields=["author", "user"],
                name="unique_subscription"
            )
        ]

    def clean(self):
        """Валидация данных модели перед их сохранением."""
        super().clean()
        if self.user == self.author:
            raise ValidationError("Нельзя подписаться на самого себя!")

    def __str__(self):
        return f"{self.user} подписан на {self.author}"


class Tag(Model):
    """Теги."""

    name = CharField(
        verbose_name="Тег",
        max_length=Limits.MAX_LEN_RECIPES_CHARFIELD.value,
        unique=True,
    )

    slug = CharField(
        verbose_name="Слаг",
        max_length=Limits.MAX_LEN_RECIPES_CHARFIELD.value,
        unique=True,
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Ingredient(Model):
    """Ингредиенты."""

    name = CharField(
        verbose_name="Ингредиент",
        max_length=Limits.MAX_LEN_RECIPES_CHARFIELD.value,
    )
    measurement_unit = CharField(
        verbose_name="Единица измерения",
        max_length=Limits.MAX_MEASUREMENT.value,
    )

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        ordering = ("name",)
        constraints = (
            UniqueConstraint(
                fields=("name", "measurement_unit"),
                name="unique_for_ingredient",
            ),
        )

    def __str__(self):
        return self.name


class Recipe(Model):
    """Модель для рецептов."""

    name = CharField(
        verbose_name="Название",
        max_length=Limits.MAX_LEN_RECIPES_CHARFIELD.value,
    )
    author = ForeignKey(
        verbose_name="Автор",
        to=User,
        on_delete=SET_NULL,
        null=True,
    )
    tags = ManyToManyField(
        verbose_name="Теги",
        to="Tag",
    )
    ingredients = ManyToManyField(
        verbose_name="Ингредиенты блюда",
        to=Ingredient,
        through="recipes.IngredientRecipe",
    )
    image = ImageField(
        verbose_name="Изображение блюда",
        upload_to="recipe_images/",
    )
    text = TextField(
        verbose_name="Описание блюда",
    )
    pub_date = DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True,
        editable=False,
    )
    cooking_time = PositiveSmallIntegerField(
        verbose_name="Время приготовления",
        default=Limits.MIN_COOKING_TIME,
        validators=(
            MinValueValidator(
                Limits.MIN_COOKING_TIME.value,
            ),
        ),
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-pub_date",)
        default_related_name = "recipes"

    def __str__(self):
        return self.name


class IngredientRecipe(Model):
    """Количество ингредиентов в блюде."""

    recipe = ForeignKey(
        verbose_name="Рецепт",
        related_name="recipe_ingredients",
        to=Recipe,
        on_delete=CASCADE,
    )
    ingredient = ForeignKey(
        verbose_name="Связанные ингредиенты",
        related_name="ingredients_in_recipe",
        to=Ingredient,
        on_delete=CASCADE,
    )
    amount = PositiveSmallIntegerField(
        verbose_name="Количество",
        default=Limits.MIN_AMOUNT_INGREDIENTS,
        validators=(
            MinValueValidator(
                Limits.MIN_AMOUNT_INGREDIENTS,
            ),
        ),
    )

    class Meta:
        verbose_name = "Продукт в рецепте"
        verbose_name_plural = "Продукты в рецепте"
        ordering = ("recipe",)
        constraints = (
            UniqueConstraint(
                fields=(
                    "recipe",
                    "ingredient",
                ),
                name="\n%(app_label)s_%(class)s ingredient alredy added\n",
            ),
        )

    def __str__(self) -> str:
        return f"{self.amount} {self.ingredient}"


class UserRecipeRelation(Model):
    """Базовый класс для связи пользователя с рецептом."""

    recipe = ForeignKey(
        verbose_name="Рецепт",
        to=Recipe,
        on_delete=CASCADE,
    )
    user = ForeignKey(
        verbose_name="Пользователь",
        to=User,
        on_delete=CASCADE,
    )

    class Meta:
        default_related_name = "%(class)ss"
        abstract = True
        constraints = (
            UniqueConstraint(
                fields=("recipe", "user"),
                name="%(app_label)s_%(class)s_unique"
            ),
        )

    def __str__(self) -> str:
        return f"{self.user} -> {self.recipe}"


class Favorite(UserRecipeRelation):
    """Избранные рецепты."""

    class Meta(UserRecipeRelation.Meta):
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"


class Cart(UserRecipeRelation):
    """Рецепты в списке покупок."""

    class Meta(UserRecipeRelation.Meta):
        verbose_name = "Рецепт в списке покупок"
        verbose_name_plural = "Рецепты в списке покупок"
