import base64

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db.models import Q, F, Sum
from django.http import FileResponse
from django.urls import reverse
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import (action)
from rest_framework.parsers import JSONParser
from rest_framework.permissions import (DjangoModelPermissions,
                                        IsAuthenticated,
                                        SAFE_METHODS)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .mixins import AddDelViewMixin
from .pagination import PageLimitPagination
from .permissions import IsAuthorOrReadOnly
from .render import render_shopping_list
from .serializers import (
    IngredientSerializer,
    TagSerializer,
    UserSubscribeSerializer,
    RecipeWriteSerializer,
    RecipeReadSerializer,
)
from recipes.additional import Tuples
from recipes.models import (Cart, Favorite,
                            Ingredient, Recipe, Subscriptions, Tag)

User = get_user_model()


class UserViewSet(DjoserUserViewSet, AddDelViewMixin):
    """Работа с пользователями."""

    pagination_class = PageLimitPagination
    permission_classes = (DjangoModelPermissions,)
    add_serializer = UserSubscribeSerializer
    link_model = Subscriptions

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id):
        """Взаимодействие между пользователями."""

    @subscribe.mapping.post
    def create_subscribe(self, request, id):
        return self._create_relation(id)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        return self._delete_relation(Q(author__id=id))

    @action(
        methods=("get",), detail=False, permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        """Список подписок."""
        pages = self.paginate_queryset(
            User.objects.filter(authors__user=self.request.user)
        )
        serializer = UserSubscribeSerializer(pages,
                                             many=True,
                                             context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['put', 'delete'],
        detail=False,
        permission_classes=[IsAuthenticated],
        parser_classes=[JSONParser],
        url_path='me/avatar'
    )
    def upload_avatar(self, request):
        """Загрузка или удаление аватара текущего пользователя."""
        user = request.user

        if request.method == 'PUT':
            avatar_data = request.data.get('avatar')
            if not avatar_data:
                return Response({'error': 'Не передано поле avatar.'},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                format, imgstr = avatar_data.split(';base64,')
                ext = format.split('/')[-1]
                avatar = ContentFile(base64.b64decode(imgstr),
                                     name=f'avatar.{ext}')
            except Exception:
                return Response({'error': 'Некорректный формат avatar.'},
                                status=status.HTTP_400_BAD_REQUEST)

            user.avatar = avatar
            user.save()
            return Response({'status': 'Аватар успешно загружен.'},
                            status=status.HTTP_200_OK)

        elif request.method == 'DELETE':
            user.avatar.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(ReadOnlyModelViewSet):
    """Теги."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthorOrReadOnly,)


class IngredientViewSet(ReadOnlyModelViewSet):
    """Ингредиенты."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def get_queryset(self):
        """Получение queryset"""
        name: str = self.request.query_params.get("name")
        queryset = self.queryset

        if not name:
            return queryset

        start_queryset = queryset.filter(name__istartswith=name)
        start_names = (ing.name for ing in start_queryset)
        contain_queryset = queryset.filter(name__icontains=name).exclude(
            name__in=start_names
        )
        return list(start_queryset) + list(contain_queryset)


class RecipeViewSet(ModelViewSet, AddDelViewMixin):
    """Работа с рецептами."""

    queryset = Recipe.objects.select_related("author")
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = PageLimitPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def get_queryset(self):
        """Получение queryset."""
        queryset = self.queryset

        tags: list = self.request.query_params.getlist("tags")
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        author: str = self.request.query_params.get("author")
        if author:
            queryset = queryset.filter(author=author)

        if self.request.user.is_anonymous:
            return queryset

        is_in_cart: str = self.request.query_params.get("is_in_shopping_cart")
        if is_in_cart in Tuples.SYMBOL_TRUE_SEARCH.value:
            queryset = queryset.filter(carts__user=self.request.user)
        elif is_in_cart in Tuples.SYMBOL_FALSE_SEARCH.value:
            queryset = queryset.exclude(carts__user=self.request.user)

        is_favorite: str = self.request.query_params.get("is_favorited")
        if is_favorite in Tuples.SYMBOL_TRUE_SEARCH.value:
            queryset = queryset.filter(favorites__user=self.request.user)
        if is_favorite in Tuples.SYMBOL_FALSE_SEARCH.value:
            queryset = queryset.exclude(favorites__user=self.request.user)

        return queryset

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        """Добавляет/удаляет рецепт в избранное."""

    @favorite.mapping.post
    def recipe_to_favorites(self, request, pk):
        self.link_model = Favorite
        self.add_serializer = RecipeReadSerializer
        return self._create_relation(pk)

    @favorite.mapping.delete
    def remove_recipe_from_favorites(self, request, pk):
        self.link_model = Favorite
        return self._delete_relation(Q(recipe__id=pk))

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        """Добавляет/удаляет рецепт в список покупок."""

    @shopping_cart.mapping.post
    def recipe_to_cart(self, request, pk):
        self.link_model = Cart
        self.add_serializer = RecipeReadSerializer
        return self._create_relation(pk)

    @shopping_cart.mapping.delete
    def remove_recipe_from_cart(self, request, pk):
        self.link_model = Cart
        return self._delete_relation(Q(recipe__id=pk))

    @action(methods=("get",), detail=False)
    def download_shopping_cart(self, request):
        """Загружает файл *.txt со списком покупок."""
        user = self.request.user

        ingredients = (
            Ingredient.objects
            .filter(ingredients_in_recipe__recipe__carts__user=user)
            .values(
                "name",
                measurement=F("measurement_unit"),
                recipe_id=F("ingredients_in_recipe__recipe_id"),
            )
            .annotate(total_amount=Sum("ingredients_in_recipe__amount"))
            .order_by("name")
        )

        recipes = Recipe.objects.filter(
            carts__user=user
        ).select_related("author")

        shopping_list_text = render_shopping_list(user, ingredients, recipes)
        filename = f"{user.username}_shopping_list.txt"

        return FileResponse(
            shopping_list_text,
            as_attachment=True,
            filename=filename,
            content_type='text/plain'
        )

    @action(
        detail=True,
        methods=["get"],
        url_path="get-link",
        permission_classes=[],
    )
    def get_link(self, request, pk):
        path = reverse('short-link-redirect', kwargs={'pk': pk})
        url = f"{settings.SITE_DOMAIN}{path}"
        return Response({"short-link": url})
