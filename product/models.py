from django.db import models
from django.contrib.auth.models import User
from django.db.models import F, Count, Sum
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver

SM = 'super-market'
HB = 'health-beauty'
HM = 'home-office'
PT = 'phones-tablet'
CM = 'computing'
EL = 'electronics'
FN = 'fashion'
FW = 'foot-wear'
BP = 'baby-products'
SG = 'sporting-goods'
AT = 'automobile'

PRODUCT_CATEGORIES = [
        (SM, 'Supermarket'),
        (HB, 'Health & Beauty'),
        (HM, 'Home and Office'),
        (PT, 'Phones & Tablet'),
        (CM, 'Computing'),
        (EL, 'Electronics'),
        (FN, 'Fashion'),
        (FW, 'Foot Wear'),
        (BP, 'Baby Products'),
        (SG, 'Sporting goods'),
        (AT, 'Automobile'),
]


class ProductTopSellingManager(models.Manager):
    def top_selling(self):
        return super().get_queryset().order_by('-quantity_sold')[:4]

    def top_footwear_trends(self):
            return super().get_queryset().filter(category=FW).order_by('-quantity_sold')[:4]

    def top_phones(self):
            return super().get_queryset().filter(category=PT).order_by('-quantity_sold')[:4]


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    rate = models.DecimalField(max_digits=4, decimal_places=2)
    review = models.CharField(max_length=1000, blank=True)
    timestamp = models.DateField(auto_now_add=True)
    
class Product(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='products')
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=14, decimal_places=2)
    discount = models.DecimalField(decimal_places=2, max_digits=4)    
    quantity_available = models.IntegerField()
    quantity_sold = models.IntegerField()
    category = models.CharField(choices=PRODUCT_CATEGORIES, max_length=40)
    ratings = models.ManyToManyField(Rating)
    express_shipping = models.BooleanField(default=False)
    shipped_from_nigeria = models.BooleanField(default=True)

    objects = ProductTopSellingManager()

    def __str__(self):
            return self.name

    @property
    def product_rating(self, _id=None):
        return self.ratings.all().aggregate(
                reviews_count=Count('user'), ratings=Sum('rate')/Count('rate')) 

    @property
    def product_reviews_count(self, _id=None):
        return self.ratings.exclude(review='').count()

    @property
    def product_reviews(self, _id=None):
        return self.ratings.exclude(review='')[:3]

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'pk':self.pk})

class CartItem(models.Model):
    product = models.ForeignKey(Product, models.CASCADE)
    quantity = models.IntegerField(default=0)

    @property
    def total_price(self):
        tp = self.product.price*((100-self.product.discount)/100)*self.quantity
        return tp
            

class UserCart(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')
    items = models.ManyToManyField(CartItem) 

    def __str__(self):
        return self.owner.username

    @property
    def total_cart_quantity(self):
        return self.items.all().aggregate(total_sum=Sum(F('quantity')))

    @property
    def total_cart_price(self):
        qs = self.items.all().aggregate(
            total_price=Sum((F('product__price')*((100-F('product__discount'))*0.01))*F('quantity'), output_field=models.DecimalField())
        )
        return qs['total_price']


class HomePageSlider(models.Model):
    image = models.ImageField(upload_to='slider')

    def __str__(self):
        return str(self.id)

    


class FavouriteProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favourites')
    products = models.ManyToManyField(Product)

    def __str__(self):
            return self.user.first_name



@receiver(post_save, sender=User)
def create_usermodel_dependencies(sender, instance, created, **kwargs):
    if created:
        UserCart.objects.create(owner=instance)
        FavouriteProduct.objects.create(user=instance)



    




