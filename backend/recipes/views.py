from django.http import Http404
from django.shortcuts import redirect

from recipes.models import Recipe


def short_link_redirect(request, pk):
    """Редирект по короткой ссылке на страницу рецепта."""
    if not Recipe.objects.filter(pk=pk).exists():
        raise Http404(f"Рецепт с ID {pk} не найден.")

    return redirect(f'/recipes/{pk}/')
