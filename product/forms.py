from django import forms
from .models import Rating, Product

class ProductReviewForm(forms.ModelForm):

    class Meta:
        model = Rating
        fields = ['rate', 'review']

    def valid(self, validated_data):
        return validated_data