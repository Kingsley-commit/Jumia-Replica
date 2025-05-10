from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, View, FormView
from .models import (
    Product, CartItem, UserCart, FavouriteProduct, Rating, HomePageSlider, PRODUCT_CATEGORIES
    )
from django.db.models import F, Count, Sum
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from django.conf import settings
from .forms import ProductReviewForm
from django.http.response import HttpResponseRedirect
from unicodedata import category

class HomePageProductListView(ListView):
    queryset = Product.objects.all()[:5]
    context_object_name = 'products'
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_sales'] = Product.objects.top_selling()
        context['top_footwear_trends'] = Product.objects.top_footwear_trends()
        context['top_phones'] = Product.objects.top_phones()
        
        return context


class ProductCategoryListView(ListView):
    queryset = Product.objects.all()
    context_object_name = 'products'
    template_name = 'product/category.html'

    def get_queryset(self, **kwargs):
        product_category = self.kwargs['product_category']
        rating = self.request.GET.get('rating')
        express_shipping = self.request.GET.get('express_shipping')
        price = self.request.GET.get('price')
        shipped_from_nigeria = self.request.GET.get('shipped_from_nigeria')
        discount_price = self.request.GET.get('discount_price')
        qs = Product.objects.filter(category=product_category)


        if rating:
            qs = qs.annotate(reviews_count=Count('ratings__user'), rating=Sum('ratings__rate')/Count('ratings__rate')).filter(
                rating__gte=rating
            )
        
        if express_shipping:
           qs = qs.filter(express_shipping=express_shipping) 
        
        if price:
           qs = qs.filter(price__lte=price) 

        if shipped_from_nigeria:
           qs = qs.filter(shipped_from_nigeria=shipped_from_nigeria) 

        if discount_price:
           qs = qs.filter(discount__gte=discount_price) 

        return qs


    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            in_cart_products_ids = UserCart.objects.get(
                owner=self.request.user).items.values_list('product__id', 'quantity')
        else:
            in_cart_products_ids = []
        context['in_cart_products_ids'] = in_cart_products_ids
        temp_category = self.kwargs['product_category']
        for category in PRODUCT_CATEGORIES:
            if category[0] == temp_category:
                context['category'] = category[1]
                break
        return context


def update_cart(request):
    
    if request.method == 'POST':
        print(request.body)
        data = json.loads(request.body)
        product_id = data.get('product_id')
        action = data.get('action')

        cart, created = UserCart.objects.get_or_create(owner=request.user)
        item_qs = cart.items.filter(product__id=product_id)
        count = 1
        print(item_qs)
        if item_qs.exists():
            item = item_qs[0]
            if action == 'increment':
                item.quantity += 1
                item.save()
                count = item.quantity
            elif action == 'decrement':
                if item.quantity == 1:
                    cart.items.remove(item)
                    count = 0
                else:
                    item.quantity -= 1
                    item.save()
                    count = item.quantity
        else:
            print(product_id, request.POST)
            product = Product.objects.get(id=product_id)
            cart.items.add(CartItem.objects.create(product=product, quantity=1)) 


        return JsonResponse({'success': True, 'quantity': count})


def get_user_cart_total(request):
    
    if request.user.is_authenticated:
        data = UserCart.objects.get(owner=request.user).total_cart_quantity
        total = data['total_sum'] if data['total_sum'] != None else 0
        return JsonResponse({'total': total})
    else:
        return JsonResponse({})

            
class ProductDetailView(DetailView):
    model = Product
    template_name = 'product/detail.html'
    context_object_name = 'product'


    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        in_cart = []
        if self.request.user.is_authenticated:
            context['favourites_ids'] = FavouriteProduct.objects.get(user=self.request.user).products.values_list('id', flat=True)
            item_qs = UserCart.objects.get(
            owner=self.request.user).items.filter(product__id=self.kwargs['pk'])
            in_cart = item_qs.exists()
            context['in_cart'] = in_cart
            print(context)
        if in_cart:
            context['item_quantity'] = item_qs.first().quantity
        else:
            context['item_quantity'] = 0
        return context


class ProductReviewsView(DetailView):
    model = Product
    template_name = 'product/reviews.html'
    context_object_name = 'product'


    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            item_qs = UserCart.objects.get(
                owner=self.request.user).items.filter(product__id=self.kwargs['pk'])
            in_cart = item_qs.exists()
            context['favourites_ids'] = FavouriteProduct.objects.get(user=self.request.user).products.values_list('id', flat=True)
        else:
            item_qs = []
            in_cart =  False
            context['favourites_ids'] = []
            
        context['in_cart'] = in_cart
        
        print(context)
        if in_cart:
            context['item_quantity'] = item_qs.first().quantity
        else:
            context['item_quantity'] = 0
        return context



def update_favourites(request):

    if request.user.is_authenticated:
        if request.method == 'POST':
            data = json.loads(request.body)
            product_id = data.get('product_id')
            user_favourites = FavouriteProduct.objects.get(user=request.user)
            product = Product.objects.get(id=product_id)
            favourites_qs = user_favourites.products.filter(id=product_id)

            if favourites_qs.exists():
                user_favourites.products.remove(product)
                action = 'remove'
            else:
                user_favourites.products.add(product)
                action = 'add'

            return JsonResponse({'success': True, 'action':action})
    else:
        return JsonResponse({})

class CartPage(LoginRequiredMixin ,ListView):
    template_name = 'product/cart_page.html'
    queryset = UserCart.objects.all()
    context_object_name = 'cart_items'
    login_url = '/account/'
    redirect_field_name = 'redirect_to'

    def get_queryset(self, **kwargs):
        qs = UserCart.objects.get(owner=self.request.user).items.all()
        return qs

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        cart = UserCart.objects.get(owner=self.request.user)
        context['cart'] = cart
        
        return context


class Checkout(LoginRequiredMixin, View):      
    template_name = 'product/checkout.html'
    login_url = '/account/'
    redirect_field_name = 'redirect_to'
    context_object_name = 'cart_items'

    def get(self, request, *args, **kwargs):
        cart = UserCart.objects.get(owner=self.request.user)
        key = settings.FLW_SANDBOX_PUBLIC_KEY
        return render(request, self.template_name, {'cart': cart, 'key':key})

    def post(self, request, *args, **kwargs):

        return render(request, self.template_name)


class ProductReviewView(FormView):
    form_class = ProductReviewForm
    template_name = 'product/create_review.html'
    success_url = reverse_lazy('index')
    has_rated = False
    rating_id = ''

    def form_valid(self, form):
        validated_data = form.cleaned_data
        pk = self.kwargs.get('pk')
        product = get_object_or_404(Product, pk=pk)
        try:
            rating = product.ratings.get(user=self.request.user)
        except Rating.DoesNotExist:
            rating = []
        if rating:
            rating.rate = validated_data.get('rate')
            rating.review = validated_data.get('review')
            rating.save()
        else:       
            rate_obj = form.save(commit=False)
            rate_obj.user = self.request.user
            rate_obj.save()
            product.ratings.add(rate_obj)
        return super(ProductReviewView, self).form_valid(form)
            

    def get_context_data(self, **kwargs):
        pk = self.kwargs.get('pk')
        product = get_object_or_404(Product, pk=pk)
        try:
            rating = product.ratings.get(user=self.request.user)
        except Rating.DoesNotExist:
            rating = []
        context = super().get_context_data(**kwargs)
        context['product'] = product
        context['rating'] = rating
        return context


class HomeSliderImagesView(View):

    def get(self, request, *args, **kwargs):
        images = list({'image': x.image.url} for x in HomePageSlider.objects.all())
        return JsonResponse(images, safe=False)


class ProductSearchView(View):

    def get(self, request, *args, **kwargs):
        context = {}
        query_param = request.GET.get('q')

        products = Product.objects.filter(name__icontains=query_param)
        if self.request.user.is_authenticated:
            in_cart_products_ids = UserCart.objects.get(
                owner=self.request.user).items.values_list('product__id', 'quantity')
        else:
            in_cart_products_ids = []
        context['in_cart_products_ids'] = in_cart_products_ids
        context['products'] = products

        return render(request, 'product/catalog.html', context)


