from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField( upload_to='profile_pics/')
    bio = models.TextField(blank=True)
    

    def __str__(self):
        return f'{self.user.username} Profile'
    

class Flower(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='flowers/')
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name


# class Category(models.Model):
#     name = models.CharField(max_length=100)

    # def __str__(self):
    #     return self.name


class Bouquet(models.Model):
    name = models.CharField(max_length=100)
    flowers = models.ManyToManyField(
        Flower, through='BouquetFlower', related_name='bouquets'
    )
    image = models.ImageField(upload_to='bouquets/')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
    @property
    def total_price(self):
        return sum(item.flower.price * item.quantity for item in self.bouquetflower_set.all())

class BouquetFlower(models.Model):
    bouquet = models.ForeignKey(Bouquet, on_delete=models.CASCADE)
    flower = models.ForeignKey(Flower, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.flower.name} in {self.bouquet.name}"





#--------------------------------------order model ------------------------------------

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bouquets = models.ManyToManyField(Bouquet, through='OrderBouquet')
    order_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

class OrderBouquet(models.Model):
      order = models.ForeignKey(Order , on_delete= models.CASCADE)
      bouquet = models.ForeignKey(Bouquet, on_delete=models.SET_NULL, null=True, blank=True)
      quantity =  models.PositiveIntegerField(default=1)
      bouquet_name = models.CharField(max_length=100, null=True, blank=True)  # added this line to know the name of bouquet deleted 
      def __str__(self):
             return f"{self.quantity} × {self.bouquet_name or 'Deleted Bouquet'} (Order {self.order.id})"