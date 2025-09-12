import json
import requests
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from products.models import Category, Product, ProductImage
from django.core.files.base import ContentFile
import urllib.request

class Command(BaseCommand):
    help = 'Populate products from FakeStore API'
    
    def handle(self, *args, **options):
        self.stdout.write('Fetching products from FakeStore API...')
        
        # Fetch categories first
        categories_url = 'https://fakestoreapi.com/products/categories'
        categories_response = requests.get(categories_url)
        categories = categories_response.json()
        
        # Create categories
        category_mapping = {}
        for category_name in categories:
            slug = slugify(category_name)
            category, created = Category.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': category_name,
                    'description': f'Products in the {category_name} category'
                }
            )
            category_mapping[category_name] = category
            if created:
                self.stdout.write(f'Created category: {category_name}')
            else:
                self.stdout.write(f'Category already exists: {category_name}')
        
        # Fetch products
        products_url = 'https://fakestoreapi.com/products'
        products_response = requests.get(products_url)
        products_data = products_response.json()
        
        # Create products
        for item in products_data:
            # Get or create the product
            slug = slugify(item['title'])
            product, created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': item['title'],
                    'description': item['description'],
                    'price': item['price'],
                    'category': category_mapping.get(item['category']),
                    'stock': 10,  # Default stock value
                    'available': True
                }
            )
            
            if created:
                self.stdout.write(f'Created product: {item["title"]}')
                
                # Create product image
                try:
                    # Get the image from the URL
                    image_url = item['image']
                    image_name = f"{slug}.jpg"
                    
                    # Create a ProductImage instance
                    product_image = ProductImage(product=product)
                    
                    # Download the image and save it
                    response = urllib.request.urlopen(image_url)
                    product_image.image.save(
                        image_name,
                        ContentFile(response.read()),
                        save=True
                    )
                    
                    self.stdout.write(f'Added image for product: {item["title"]}')
                except Exception as e:
                    self.stdout.write(f'Error adding image for {item["title"]}: {str(e)}')
            else:
                self.stdout.write(f'Product already exists: {item["title"]}')
        
        self.stdout.write(self.style.SUCCESS('Successfully populated products from FakeStore API'))