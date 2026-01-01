---
name: Flower Order Management System
overview: Build a full-stack flower order management system with React SPA frontend and FastAPI backend, including user authentication, flower inventory management, customer management, and order tracking.
todos:
  - id: backend-setup
    content: "Set up FastAPI backend structure: create project folders, install dependencies (FastAPI, SQLAlchemy async, Alembic, Pydantic, python-jose, passlib, asyncpg, aioredis), configure async database connection, Redis connection, and JWT settings"
    status: pending
  - id: backend-redis-setup
    content: "Set up Redis connection and cache service: create Redis client with aioredis, implement cache utilities for session management and data caching (flowers, customers, orders lists)"
    status: pending
    dependencies:
      - backend-setup
  - id: backend-models
    content: Create async SQLAlchemy models for User, Flower, Customer, Order, and OrderItem with proper relationships and constraints
    status: pending
    dependencies:
      - backend-setup
  - id: backend-schemas
    content: Create Pydantic schemas for all entities (create, update, response variants) with validation
    status: pending
    dependencies:
      - backend-models
  - id: backend-auth
    content: "Implement authentication endpoints: login endpoint with JWT token generation, password hashing utilities, JWT dependency for protected routes, and Redis session storage for token blacklisting"
    status: pending
    dependencies:
      - backend-schemas
      - backend-redis-setup
  - id: backend-flowers-api
    content: "Implement flowers API endpoints: async CRUD operations and stock update endpoint with proper error handling, implement Redis caching for flower lists and individual flower lookups"
    status: pending
    dependencies:
      - backend-auth
      - backend-redis-setup
  - id: backend-customers-api
    content: "Implement customers API endpoints: async CRUD operations with validation, implement Redis caching for customer lists and individual customer lookups"
    status: pending
    dependencies:
      - backend-auth
      - backend-redis-setup
  - id: backend-orders-api
    content: "Implement orders API endpoints: async create, list (with status filter), get details, and update status, implement Redis caching for order lists with cache invalidation on updates"
    status: pending
    dependencies:
      - backend-flowers-api
      - backend-customers-api
      - backend-redis-setup
  - id: backend-migrations
    content: "Create Alembic migrations: initial migration with all tables and relationships"
    status: pending
    dependencies:
      - backend-models
  - id: docker-setup
    content: Create Dockerfile for backend service with proper Python setup, dependencies, and configuration for connecting to external PostgreSQL and Redis instances
    status: pending
  - id: frontend-setup
    content: "Set up React frontend: create project with Vite, install dependencies (React Router, Axios, Formik, Zod, Tailwind v4, shadcn/ui), configure Tailwind and shadcn"
    status: pending
  - id: frontend-api-service
    content: "Create API service layer: Axios instance with interceptors for JWT token and error handling"
    status: pending
    dependencies:
      - frontend-setup
  - id: frontend-auth-context
    content: "Implement AuthContext: login/logout functions, token management, protected route wrapper"
    status: pending
    dependencies:
      - frontend-api-service
  - id: frontend-contexts
    content: Create Context providers for Flowers, Customers, and Orders with CRUD operations
    status: pending
    dependencies:
      - frontend-auth-context
  - id: frontend-login-page
    content: "Build Login page: form with Formik + Zod validation, error handling, redirect on success"
    status: pending
    dependencies:
      - frontend-auth-context
  - id: frontend-flowers-page
    content: "Build Flowers management page: table view, add/edit dialogs with forms, delete confirmation, stock update functionality"
    status: pending
    dependencies:
      - frontend-contexts
  - id: frontend-customers-page
    content: "Build Customers management page: table view, add/edit dialogs with forms, delete confirmation"
    status: pending
    dependencies:
      - frontend-contexts
  - id: frontend-orders-page
    content: "Build Orders page: table view with status filter, order details view, status update functionality"
    status: pending
    dependencies:
      - frontend-contexts
  - id: frontend-layout
    content: "Create main layout: navigation sidebar/menu, header with user info and logout, route protection"
    status: pending
    dependencies:
      - frontend-login-page
  - id: integration-testing
    content: "Test end-to-end: verify all CRUD operations work, test authentication flow, verify order creation with items"
    status: pending
    dependencies:
      - frontend-flowers-page
      - frontend-customers-page
      - frontend-orders-page
      - frontend-layout
---

# Flower Order Management System -

Implementation Plan

## Architecture Overview

The application will consist of:

- **Frontend**: React SPA with Tailwind v4 + shadcn/ui, Context API for state, Formik + Zod for forms
- **Backend**: FastAPI REST API with JWT authentication, async database operations
- **Database**: PostgreSQL for primary data storage (async with asyncpg + SQLAlchemy async)
- **Cache**: Redis for session management, token blacklisting, and data caching (mandatory, async with aioredis)

## Project Structure

```javascript
flora-agent/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── auth.py
│   │   │   │   │   ├── flowers.py
│   │   │   │   │   ├── customers.py
│   │   │   │   │   └── orders.py
│   │   │   │   └── deps.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   ├── database.py
│   │   │   └── redis.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── flower.py
│   │   │   ├── customer.py
│   │   │   └── order.py
│   │   ├── schemas/
│   │   │   ├── user.py
│   │   │   ├── flower.py
│   │   │   ├── customer.py
│   │   │   └── order.py
│   │   ├── services/
│   │   │   ├── auth.py
│   │   │   ├── flower.py
│   │   │   ├── customer.py
│   │   │   └── order.py
│   │   └── main.py
│   ├── alembic/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/ (shadcn components)
│   │   │   ├── flowers/
│   │   │   ├── customers/
│   │   │   ├── orders/
│   │   │   └── layout/
│   │   ├── contexts/
│   │   │   ├── AuthContext.tsx
│   │   │   ├── FlowerContext.tsx
│   │   │   ├── CustomerContext.tsx
│   │   │   └── OrderContext.tsx
│   │   ├── pages/
│   │   │   ├── Login.tsx
│   │   │   ├── Flowers.tsx
│   │   │   ├── Customers.tsx
│   │   │   └── Orders.tsx
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── hooks/
│   │   │   └── useAuth.ts
│   │   ├── utils/
│   │   │   └── validation.ts
│   │   └── App.tsx
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```



## Database Schema

### Users Table

- `id` (UUID, primary key)
- `username` (string, unique)
- `hashed_password` (string)
- `is_active` (boolean, default true)
- `created_at` (timestamp)
- `updated_at` (timestamp)

### Flowers Table

- `id` (UUID, primary key)
- `name` (string)
- `description` (text, nullable)
- `price` (decimal)
- `stock_quantity` (integer)
- `created_at` (timestamp)
- `updated_at` (timestamp)

### Customers Table

- `id` (UUID, primary key)
- `name` (string)
- `email` (string, unique, nullable)
- `phone` (string)
- `address` (text, nullable)
- `created_at` (timestamp)
- `updated_at` (timestamp)

### Orders Table

- `id` (UUID, primary key)
- `customer_id` (UUID, foreign key)
- `status` (enum: 'ordered', 'delivered')
- `created_at` (timestamp)
- `updated_at` (timestamp)

### Order Items Table

- `id` (UUID, primary key)
- `order_id` (UUID, foreign key)
- `flower_id` (UUID, foreign key)
- `quantity` (integer)
- `price_at_time` (decimal) - snapshot of price when ordered

## Backend Implementation

### Core Setup ([backend/app/core/](backend/app/core/))

- **config.py**: Environment variables, async database URLs, Redis URLs, JWT settings
- **database.py**: Async SQLAlchemy setup with asyncpg, async session management
- **redis.py**: Async Redis client setup with aioredis, connection pool management
- **security.py**: Password hashing, JWT token generation/verification

### Models ([backend/app/models/](backend/app/models/))

- Async SQLAlchemy models for User, Flower, Customer, Order, OrderItem
- Relationships: Order → Customer, Order → OrderItems → Flower
- All database operations use async/await pattern

### Schemas ([backend/app/schemas/](backend/app/schemas/))

- Pydantic schemas for request/response validation
- Separate schemas for create, update, and response operations

### API Endpoints ([backend/app/api/v1/endpoints/](backend/app/api/v1/endpoints/))

All endpoints use async/await pattern for database and Redis operations.

- **auth.py**: 
- POST `/api/v1/auth/login` (returns JWT token, stores in Redis for blacklisting)
- **flowers.py**: 
- GET `/api/v1/flowers` (list with pagination, cached in Redis)
- POST `/api/v1/flowers` (create, invalidates cache)
- GET `/api/v1/flowers/{id}` (get one, cached in Redis)
- PUT `/api/v1/flowers/{id}` (update, invalidates cache)
- DELETE `/api/v1/flowers/{id}` (delete, invalidates cache)
- PATCH `/api/v1/flowers/{id}/stock` (update stock, invalidates cache)
- **customers.py**: Similar async CRUD operations with Redis caching
- **orders.py**: 
- GET `/api/v1/orders` (list with filters for status, cached in Redis)
- POST `/api/v1/orders` (create, invalidates cache)
- GET `/api/v1/orders/{id}` (get details with items, cached in Redis)
- PATCH `/api/v1/orders/{id}/status` (update status, invalidates cache)

### Redis Integration ([backend/app/core/redis.py](backend/app/core/redis.py))

- Async Redis client initialization and connection pool using aioredis
- Cache utilities for:
- **Session management**: JWT token blacklisting (key: `blacklist:{token_jti}`, TTL: token expiry)
- **Flower list caching**: Cache paginated flower lists (key: `flowers:list:{page}:{limit}`, TTL: 300s)
- **Flower detail caching**: Cache individual flower lookups (key: `flower:{id}`, TTL: 600s)
- **Customer list caching**: Cache paginated customer lists (key: `customers:list:{page}:{limit}`, TTL: 300s)
- **Customer detail caching**: Cache individual customer lookups (key: `customer:{id}`, TTL: 600s)
- **Order list caching**: Cache filtered order lists (key: `orders:list:{status}:{page}:{limit}`, TTL: 180s)
- **Order detail caching**: Cache order details with items (key: `order:{id}`, TTL: 300s)
- Cache invalidation strategies:
- On flower create/update/delete: Invalidate `flowers:list:*` and `flower:{id}`
- On customer create/update/delete: Invalidate `customers:list:*` and `customer:{id}`
- On order create/update: Invalidate `orders:list:*` and `order:{id}`
- Helper functions: `get_cache`, `set_cache`, `delete_cache`, `invalidate_pattern`

### Dependencies ([backend/app/api/v1/deps.py](backend/app/api/v1/deps.py))

- `get_current_user`: Async JWT token verification, Redis blacklist check, and user extraction
- Async database session dependency
- Redis client dependency

## Frontend Implementation

### Authentication ([frontend/src/contexts/AuthContext.tsx](frontend/src/contexts/AuthContext.tsx))

- Context provider for auth state
- Login/logout functions
- Token storage in localStorage
- Protected route wrapper

### State Management ([frontend/src/contexts/](frontend/src/contexts/))

- **FlowerContext.tsx**: CRUD operations for flowers
- **CustomerContext.tsx**: CRUD operations for customers
- **OrderContext.tsx**: Fetch and display orders

### Pages ([frontend/src/pages/](frontend/src/pages/))

- **Login.tsx**: Login form with Formik + Zod validation
- **Flowers.tsx**: 
- Table/list view of flowers
- Add/Edit modal/dialog
- Delete confirmation
- Stock update functionality
- **Customers.tsx**: Similar structure for customer management
- **Orders.tsx**: 
- Table view with status filter
- Order details view
- Status update (ordered → delivered)

### UI Components ([frontend/src/components/ui/](frontend/src/components/ui/))

- Install shadcn/ui components: Button, Table, Dialog, Form, Input, Select, Badge
- Use Tailwind v4 for styling

### API Service ([frontend/src/services/api.ts](frontend/src/services/api.ts))

- Axios instance with base URL
- Request interceptor for JWT token
- Response interceptor for error handling

## Infrastructure

### Dockerfile ([backend/Dockerfile](backend/Dockerfile))

- Python base image
- Install dependencies from requirements.txt
- Configure for connecting to external PostgreSQL and Redis instances
- Expose FastAPI port

### Database Migrations

- Alembic for database migrations (async support)
- Initial migration with all tables
- Note: PostgreSQL and Redis instances are expected to be running externally

## Key Features

1. **JWT Authentication**: Token-based auth with secure password hashing
2. **Flower Management**: Full CRUD + stock quantity management
3. **Customer Management**: Full CRUD with contact information
4. **Order Management**: View orders, filter by status, update status
5. **Responsive UI**: Modern, clean interface with shadcn/ui components
6. **Form Validation**: Formik + Zod for client-side validation
7. **Error Handling**: Proper error messages and loading states

## Technology Stack

- **Backend**: FastAPI, SQLAlchemy, Alembic, Pydantic, python-jose (JWT), passlib (password hashing)
- **Backend**: FastAPI, SQLAlchemy (async with asyncpg), Alembic (async), Pydantic, python-jose (JWT), passlib (password hashing), aioredis (async Redis client)
- **Frontend**: React, TypeScript, Tailwind CSS v4, shadcn/ui, Formik, Zod, Axios, React Router
- **Database**: PostgreSQL (async operations with asyncpg)