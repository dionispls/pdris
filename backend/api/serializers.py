"""Модуль сериализаторов для работы с
моделями пользователя, рецептов, ингредиентов и тегов."""
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db.transaction import atomic
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Ingredient, Recipe, Tag, IngredientRecipe
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework.fields import IntegerField, ReadOnlyField, ImageField

from recipes.additional import Limits

User = get_user_model()


class ShortRecipeSerializer(ModelSerializer):
    """Сериализатор для модели Recipe,
    когда нужны лишь базовые данные о рецепте."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = 'id', 'name', 'image', 'cooking_time'
        read_only_fields = fields


class UserSerializer(DjoserUserSerializer):
    """Сериализатор для отображения пользователя."""

    is_subscribed = SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        fields = DjoserUserSerializer.Meta.fields + ('is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        """Проверка подписок."""
        request = self.context.get('request')
        if not request or request.user.is_anonymous or (request.user == obj):
            return False
        return request.user.subscribers.filter(author=obj).exists()


class UserSubscribeSerializer(UserSerializer):
    """Сериализатор, расширяющий UserSerializer для отображения подписок."""

    is_subscribed = SerializerMethodField()
    recipes = SerializerMethodField()
    recipes_count = IntegerField(source='recipes.count')

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )
        read_only_fields = fields

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = ShortRecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data


class TagSerializer(ModelSerializer):
    """Сериализатор для вывода тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientInRecipeReadSerializer(ModelSerializer):
    """Сериализатор для вывода ингредиентов в рецепте."""
    id = IntegerField(source='ingredient.id', read_only=True)
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = fields


class RecipeReadSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeReadSerializer(
        source='recipe_ingredients',
        many=True,
        read_only=True
    )
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = fields

    def get_is_favorited(self, recipe):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return request.user.favorites.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return request.user.carts.filter(recipe=recipe).exists()


class IngredientInRecipeWriteSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient',
        write_only=True
    )
    amount = IntegerField(
        write_only=True,
        validators=[MinValueValidator(Limits.MIN_AMOUNT_INGREDIENTS.value)],
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeWriteSerializer(ModelSerializer):
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                  many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeWriteSerializer(many=True)
    image = Base64ImageField()
    cooking_time = IntegerField(min_value=Limits.MIN_COOKING_TIME.value)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_ingredients(self, value):
        ingredients = value
        if not ingredients:
            raise ValidationError({
                'ingredients': 'Нужен хотя бы один ингредиент!'
            })
        ingredient_ids = [item['ingredient'].id for item in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise ValidationError({
                'ingredients': 'Ингредиенты должны быть уникальными!'
            })
        return value

    def validate_tags(self, value):
        tags = value
        if not tags:
            raise ValidationError({'tags': 'Нужно выбрать хотя бы один тег!'})
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise ValidationError(
                    {'tags': 'Теги должны быть уникальными!'}
                )
            tags_list.append(tag)
        return value

    @staticmethod
    def recipe_ingredients_set(recipe, ingredients):
        """Записывает ингредиенты, вложенные в рецепт."""
        objs = [
            IngredientRecipe(
                recipe=recipe,
                ingredient_id=ingredient['ingredient'].id,
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ]
        IngredientRecipe.objects.bulk_create(objs)

    @atomic
    def create(self, validated_data):
        """Создаёт рецепт."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = super().create(validated_data)
        recipe.tags.set(tags)
        self.recipe_ingredients_set(recipe, ingredients)
        return recipe

    @atomic
    def update(self, instance, validated_data):
        """Обновляет рецепт."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.recipe_ingredients_set(recipe=instance, ingredients=ingredients)
        instance = super().update(instance, validated_data)
        return instance


class AvatarSerializer(ModelSerializer):
    avatar = ImageField()

    class Meta:
        model = User
        fields = ('avatar',)
