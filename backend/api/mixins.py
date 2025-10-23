from django.db.models import Q
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)

from recipes.models import Subscriptions

from recipes.models import User


class AddDelViewMixin:
    """ Миксин. """

    add_serializer = None
    link_model = None

    def _create_relation(self, obj_id):
        """Добавляет связь M2M между объектами."""
        if self.link_model == Subscriptions:
            obj = get_object_or_404(User, pk=obj_id)
            user = self.request.user
            try:
                self.link_model.objects.create(user=user, author=obj)
            except IntegrityError:
                return Response(
                    {"errors": "Вы уже подписаны на этого пользователя."},
                    status=HTTP_400_BAD_REQUEST,
                )
        else:
            obj = get_object_or_404(self.queryset, pk=obj_id)
            user = self.request.user
            try:
                self.link_model.objects.create(user=user, recipe=obj)
            except IntegrityError:
                return Response(
                    {"errors": "Действие уже выполнено ранее."},
                    status=HTTP_400_BAD_REQUEST,
                )

        serializer = self.add_serializer(
            obj, context={'request': self.request, 'user': self.request.user}
        )
        return Response(serializer.data, status=HTTP_201_CREATED)

    def _delete_relation(self, q):
        """Удаляет связь M2M между пользователем и объектом."""
        deleted, _ = (
            self.link_model.objects.filter(q & Q(user=self.request.user))
            .delete()
        )
        if not deleted:
            return Response(
                {"errors": f"{self.link_model.__name__} не существует."},
                status=HTTP_400_BAD_REQUEST,
            )
        return Response(status=HTTP_204_NO_CONTENT)
