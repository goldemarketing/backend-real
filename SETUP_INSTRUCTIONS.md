# Four Seasons Real Estate Hub - Setup Instructions

## Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

## Installation Steps

### 1. Navigate to the backend directory
```bash
cd back-end
```

### 2. Create and activate virtual environment (if not already done)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run database migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a superuser (admin account)
```bash
python manage.py createsuperuser
```

### 6. Collect static files
```bash
python manage.py collectstatic
```

### 7. Run the development server
```bash
python manage.py runserver
```

The API will be available at:
- Admin API: http://localhost:8000/api/admin/
- Public API: http://localhost:8000/api/public/
- Admin Dashboard: http://localhost:8000/admin/
- API Documentation: http://localhost:8000/api/

## API Testing

### Test Authentication
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'
```

### Test Public API
```bash
# Get all properties
curl http://localhost:8000/api/public/properties/

# Get featured properties
curl http://localhost:8000/api/public/properties/featured/

# Search properties
curl "http://localhost:8000/api/public/properties/?search=luxury&min_price=1000000"
```

### Test Admin API (with authentication)
```bash
# Get auth token first
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}' | jq -r '.token')

# Get all properties (admin)
curl -H "Authorization: Token $TOKEN" http://localhost:8000/api/admin/properties/

# Create new property
curl -X POST http://localhost:8000/api/admin/properties/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Property",
    "property_type": "Apartment",
    "price": "2000000.00",
    "area": 100,
    "bedrooms": 2,
    "bathrooms": 2,
    "description": "Beautiful test property"
  }'
```

## Next.js Frontend Integration

### 1. Install dependencies in frontend
```bash
cd ../front-end
npm install
```

### 2. Update API base URL in frontend
Update the API base URL in your frontend configuration to point to:
```
http://localhost:8000/api/public/
```

### 3. Example API calls from Next.js
```javascript
// pages/api/properties.js
export default async function handler(req, res) {
  const response = await fetch('http://localhost:8000/api/public/properties/');
  const data = await response.json();
  res.status(200).json(data);
}

// pages/properties/index.js
import { useState, useEffect } from 'react';

export default function Properties() {
  const [properties, setProperties] = useState([]);

  useEffect(() => {
    fetch('http://localhost:8000/api/public/properties/')
      .then(res => res.json())
      .then(data => setProperties(data.results));
  }, []);

  return (
    <div>
      {properties.map(property => (
        <div key={property.id}>
          <h2>{property.title}</h2>
          <p>{property.property_type} - {property.area} sqm</p>
          <p>Price: EGP {property.price}</p>
        </div>
      ))}
    </div>
  );
}
```

## Features Implemented

### ✅ Admin Authentication
- Token-based authentication for admin operations
- Session-based authentication for admin dashboard
- User management system

### ✅ Public API Endpoints
- Read-only endpoints for frontend consumption
- No authentication required for public endpoints
- Optimized for Next.js integration

### ✅ Rich Text Support
- CKEditor integration for description fields
- HTML content support in API responses
- WYSIWYG editing in admin dashboard

### ✅ Advanced Filtering & Search
- Text search across multiple fields
- Price range filtering
- Area range filtering
- Property type filtering
- Location and developer filtering
- Custom ordering options

### ✅ Inline Relationships
- Property images included in property details
- Amenities included in compound and property details
- Related objects serialized inline for performance

### ✅ Admin Dashboard Enhancements
- Rich text editors for content fields
- Image previews in list views
- Inline editing for related objects
- Advanced filtering and search
- Custom admin site branding

### ✅ CORS Configuration
- Configured for Next.js development server
- Credentials support for authenticated requests

### ✅ Media File Handling
- Proper media URL configuration
- Image upload support
- Static file serving in development

## Database Schema

The API supports the following models:
- **Developer**: Real estate development companies
- **Location**: Geographical areas
- **Compound**: Residential compounds/projects
- **Property**: Individual real estate units
- **PropertyImage**: Gallery images for properties
- **Amenity**: Reusable amenities list
- **Author**: Blog post authors
- **BlogPost**: Blog content
- **Partner**: Partner companies
- **Testimonial**: Client testimonials
- **ContactFormSubmission**: Contact form submissions

## API Endpoints Summary

### Admin Endpoints (Authentication Required)
- `/api/admin/properties/` - Property CRUD operations
- `/api/admin/compounds/` - Compound CRUD operations
- `/api/admin/developers/` - Developer CRUD operations
- `/api/admin/blog-posts/` - Blog post CRUD operations
- `/api/admin/locations/` - Location management
- `/api/admin/amenities/` - Amenity management
- `/api/admin/authors/` - Author management
- `/api/admin/partners/` - Partner management
- `/api/admin/testimonials/` - Testimonial management
- `/api/admin/contact-submissions/` - Contact form submissions
- `/api/admin/users/` - User management

### Public Endpoints (No Authentication Required)
- `/api/public/properties/` - List and view properties
- `/api/public/compounds/` - List and view compounds
- `/api/public/developers/` - List and view developers
- `/api/public/blog-posts/` - List and view blog posts

### Authentication Endpoints
- `/api/auth/login/` - Admin login and token generation

## Troubleshooting

### Common Issues

1. **CKEditor import errors**: Make sure to install dependencies with `pip install -r requirements.txt`

2. **CORS errors**: Ensure the frontend URL is added to `CORS_ALLOWED_ORIGINS` in settings.py

3. **Media files not loading**: Check that `MEDIA_URL` and `MEDIA_ROOT` are properly configured

4. **Database errors**: Run migrations with `python manage.py migrate`

5. **Permission errors**: Ensure the admin user has proper permissions

### Support
For issues or questions, refer to the API documentation in `API_DOCUMENTATION.md` or check the Django REST Framework documentation.

