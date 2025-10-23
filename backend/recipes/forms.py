from django import forms
from .models import IngredientRecipe


class IngredientRecipeInlineForm(forms.ModelForm):
    class Meta:
        model = IngredientRecipe
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ingredient'].label_from_instance = (
            lambda obj: f"{obj.name} ({obj.measurement_unit})"
        )
