# Catalogue - E-commerce Website

A full-featured e-commerce website built with Django, offering a seamless shopping experience with modern UI/UX design.

## Features

### Product Management
- Product catalog with categories
- Detailed product pages with image galleries
- Product search and filtering
- Stock management
- Product reviews and ratings

### Shopping Experience
- Shopping cart functionality
- User-friendly product browsing
- Responsive design for all devices
- Quick view and detailed product information
- Product image zoom and gallery

### User Management
- User registration and authentication
- User profiles
- Order history
- Review management

### Admin Dashboard
- Product management interface
- Order management system
- Category management
- User management
- Stock tracking

### Cart & Checkout
- Session-based shopping cart
- Add/remove products
- Update quantities
- Secure checkout process
- Order tracking

### Technical Features
- Django 5.2+ based
- Responsive Bootstrap-based frontend
- SQLite database (easily adaptable to other databases)
- Image upload and management
- Slug-based URLs for SEO
- Security features (CSRF, XSS protection)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ProjjwalRoyChowdhury/Catalogue.git
cd Catalogue
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Project Structure

```
ecommerce_website/
├── accounts/        # User authentication and profiles
├── cart/           # Shopping cart functionality
├── catalogue/      # Core product catalog
├── dashboard/      # Admin dashboard interface
├── orders/         # Order processing
├── payment/        # Payment processing
├── products/       # Product management
└── templates/      # HTML templates
```

## Configuration

The main settings are in `ecommerce_website/settings.py`. Key settings include:

- `CART_SESSION_ID`: Cart session identifier
- `MEDIA_ROOT`: Product image storage location
- `STATIC_ROOT`: Static files location

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the [LICENSE](LICENSE) file.

## Support

For support, please open an issue in the GitHub repository.