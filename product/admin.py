from django.contrib import admin
from .models import Product, Rating, UserCart, FavouriteProduct, HomePageSlider


admin.site.register(Product)
admin.site.register(Rating)
admin.site.register(UserCart)
admin.site.register(HomePageSlider)
admin.site.register(FavouriteProduct)