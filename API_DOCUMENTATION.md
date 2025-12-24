# Four Seasons Real Estate Hub - API Documentation

## Overview
This Django REST API provides comprehensive endpoints for managing real estate properties, compounds, developers, and blog content. The API is designed to support both admin operations and public frontend consumption.

## Base URL
- Development: `http://localhost:8000/api/`
- Admin API: `http://localhost:8000/api/admin/`
- Public API: `http://localhost:8000/api/public/`

## Authentication
The API uses token-based authentication for admin operations.

### Login
```
POST /api/auth/login/
Content-Type: application/json

{
    "username": "admin",
    "password": "password"
}
```

**Response:**
```json
{
    "token": "your-auth-token",
    "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "first_name": "",
        "last_name": "",
        "is_staff": true
    }
}
```

### Using the Token
Include the token in the Authorization header:
```
Authorization: Token your-auth-token
```

## Admin API Endpoints

### Properties
- `GET /api/admin/properties/` - List all properties
- `POST /api/admin/properties/` - Create new property
- `GET /api/admin/properties/{id}/` - Get property details
- `PUT /api/admin/properties/{id}/` - Update property
- `PATCH /api/admin/properties/{id}/` - Partial update property
- `DELETE /api/admin/properties/{id}/` - Delete property
- `GET /api/admin/properties/featured/` - Get featured properties
- `GET /api/admin/properties/new-launches/` - Get new launch properties

**Query Parameters:**
- `search` - Search in title and description
- `property_type` - Filter by property type
- `compound` - Filter by compound ID
- `developer` - Filter by developer ID
- `location` - Filter by location ID
- `is_featured` - Filter featured properties
- `is_new_launch` - Filter new launch properties
- `min_price` - Minimum price filter
- `max_price` - Maximum price filter
- `min_area` - Minimum area filter
- `max_area` - Maximum area filter
- `bedrooms` - Filter by number of bedrooms
- `bathrooms` - Filter by number of bathrooms
- `ordering` - Order by field (e.g., `price`, `-price`, `area`, `-area`)

### Compounds
- `GET /api/admin/compounds/` - List all compounds
- `POST /api/admin/compounds/` - Create new compound
- `GET /api/admin/compounds/{id}/` - Get compound details
- `PUT /api/admin/compounds/{id}/` - Update compound
- `PATCH /api/admin/compounds/{id}/` - Partial update compound
- `DELETE /api/admin/compounds/{id}/` - Delete compound
- `GET /api/admin/compounds/{id}/properties/` - Get compound properties

### Developers
- `GET /api/admin/developers/` - List all developers
- `POST /api/admin/developers/` - Create new developer
- `GET /api/admin/developers/{id}/` - Get developer details
- `PUT /api/admin/developers/{id}/` - Update developer
- `PATCH /api/admin/developers/{id}/` - Partial update developer
- `DELETE /api/admin/developers/{id}/` - Delete developer
- `GET /api/admin/developers/{id}/compounds/` - Get developer compounds

### Blog Posts
- `GET /api/admin/blog-posts/` - List all blog posts
- `POST /api/admin/blog-posts/` - Create new blog post
- `GET /api/admin/blog-posts/{id}/` - Get blog post details
- `PUT /api/admin/blog-posts/{id}/` - Update blog post
- `PATCH /api/admin/blog-posts/{id}/` - Partial update blog post
- `DELETE /api/admin/blog-posts/{id}/` - Delete blog post

### Other Admin Endpoints
- `GET /api/admin/locations/` - List locations
- `GET /api/admin/amenities/` - List amenities
- `GET /api/admin/authors/` - List authors
- `GET /api/admin/partners/` - List partners
- `GET /api/admin/testimonials/` - List testimonials
- `GET /api/admin/contact-submissions/` - List contact submissions (admin only)
- `GET /api/admin/users/` - List users (admin only)

## Public API Endpoints

### Properties (Public)
- `GET /api/public/properties/` - List all published properties
- `GET /api/public/properties/{id}/` - Get property details
- `GET /api/public/properties/featured/` - Get featured properties
- `GET /api/public/properties/new-launches/` - Get new launch properties

**Query Parameters:** Same as admin properties endpoint

### Compounds (Public)
- `GET /api/public/compounds/` - List all compounds
- `GET /api/public/compounds/{id}/` - Get compound details

### Developers (Public)
- `GET /api/public/developers/` - List all developers
- `GET /api/public/developers/{id}/` - Get developer details

### Blog Posts (Public)
- `GET /api/public/blog-posts/` - List published blog posts
- `GET /api/public/blog-posts/{id}/` - Get blog post details

## Data Models

### Property
```json
{
    "id": 1,
    "title": "Luxury Apartment in New Cairo",
    "slug": "luxury-apartment-new-cairo",
    "compound": {
        "id": 1,
        "name": "Palm Hills",
        "slug": "palm-hills"
    },
    "developer": {
        "id": 1,
        "name": "Palm Hills Development",
        "slug": "palm-hills-development"
    },
    "location": {
        "id": 1,
        "name": "New Cairo",
        "slug": "new-cairo"
    },
    "property_type": "Apartment",
    "price": "2500000.00",
    "area": 120,
    "bedrooms": 3,
    "bathrooms": 2,
    "description": "<p>Beautiful luxury apartment...</p>",
    "main_image": "/media/properties/main_images/apartment1.jpg",
    "floor_plan_image": "/media/properties/floor_plans/plan1.jpg",
    "map_image": "/media/properties/maps/map1.jpg",
    "is_new_launch": true,
    "is_featured": false,
    "amenities": [
        {"id": 1, "name": "Swimming Pool"},
        {"id": 2, "name": "Gym"}
    ],
    "gallery_images": [
        {
            "id": 1,
            "image": "/media/properties/gallery_images/gallery1.jpg",
            "alt_text": "Living room"
        }
    ]
}
```

### Compound
```json
{
    "id": 1,
    "name": "Palm Hills New Cairo",
    "slug": "palm-hills-new-cairo",
    "developer": {
        "id": 1,
        "name": "Palm Hills Development",
        "slug": "palm-hills-development"
    },
    "location": {
        "id": 1,
        "name": "New Cairo",
        "slug": "new-cairo"
    },
    "main_image": "/media/compounds/main_images/compound1.jpg",
    "description": "<p>Luxury residential compound...</p>",
    "status": "Ready to Move",
    "delivery_date": "Q4 2024",
    "amenities": [
        {"id": 1, "name": "Swimming Pool"},
        {"id": 2, "name": "Gym"},
        {"id": 3, "name": "Clubhouse"}
    ]
}
```

### Developer
```json
{
    "id": 1,
    "name": "Palm Hills Development",
    "slug": "palm-hills-development",
    "logo": "/media/developers/logos/palm-hills-logo.jpg",
    "description": "<p>Leading real estate developer...</p>",
    "projects_count": 5
}
```

### Blog Post
```json
{
    "id": 1,
    "title": "Real Estate Market Trends 2024",
    "slug": "real-estate-market-trends-2024",
    "excerpt": "An overview of the latest trends...",
    "content": "<p>Detailed blog content...</p>",
    "publish_date": "2024-01-15T10:30:00Z",
    "image": "/media/blog/images/trends-2024.jpg",
    "author_name": "John Doe",
    "author_picture": "/media/authors/pictures/john-doe.jpg"
}
```

## Error Responses

### 400 Bad Request
```json
{
    "field_name": ["This field is required."]
}
```

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
    "detail": "Not found."
}
```

## Pagination
All list endpoints support pagination:

```json
{
    "count": 100,
    "next": "http://localhost:8000/api/properties/?page=2",
    "previous": null,
    "results": [...]
}
```

## Media Files
All image fields return full URLs when accessed via API. Make sure to configure `MEDIA_URL` and `MEDIA_ROOT` in Django settings.

## CORS Configuration
The API is configured to allow requests from:
- `http://localhost:3000` (Next.js development server)
- `http://127.0.0.1:3000`

## Next.js Integration Examples

### Fetching Properties
```javascript
// Get all properties
const response = await fetch('http://localhost:8000/api/public/properties/');
const data = await response.json();

// Get featured properties
const featured = await fetch('http://localhost:8000/api/public/properties/featured/');
const featuredData = await featured.json();

// Search properties
const search = await fetch('http://localhost:8000/api/public/properties/?search=luxury&min_price=1000000');
const searchData = await search.json();
```

### Fetching Property Details
```javascript
const property = await fetch('http://localhost:8000/api/public/properties/1/');
const propertyData = await property.json();
```

### Admin Operations (with authentication)
```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/api/auth/login/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        username: 'admin',
        password: 'password'
    })
});
const { token } = await loginResponse.json();

// Create property
const newProperty = await fetch('http://localhost:8000/api/admin/properties/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${token}`
    },
    body: JSON.stringify({
        title: 'New Property',
        property_type: 'Apartment',
        price: '2000000.00',
        area: 100,
        bedrooms: 2,
        bathrooms: 2,
        description: 'Beautiful apartment...'
    })
});
```

