from django.db import models
from django.urls import reverse
from category.models import Category


class Product(models.Model):

    product_name = models.TextField(max_length=100,unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(max_length=50, blank=True)
    price = models.IntegerField()
    images = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    
    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name



# to save slugs using title fields and has an increment for ensuring uniqueness
# def save(self, *args, **kwargs):
#     if not self.slug:
#         base_slug = slugify(self.title)
#         slug = base_slug
#         count = 1

#         while Article.objects.filter(slug=slug).exists():
#             slug = f"{base_slug}-{count}"
#             count += 1

#         self.slug = slug

#     super().save(*args, **kwargs)

