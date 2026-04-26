# StayEase API — Sample JSON Test Data

> **Base URL:** `http://127.0.0.1:8000/api/v1`  
> **Tool:** Use Postman, Insomnia, or `curl`  
> **Auth header:** `Authorization: Bearer <access_token>`  
> **Content-Type:** `application/json` (except image uploads — use `multipart/form-data`)

---

## Recommended Testing Order

```
1. Register         → get tokens
2. Login as admin   → get admin tokens
3. Create Amenities → get amenity IDs
4. Create Policies  → get policy IDs
5. Create Room      → get room ID
6. Browse Rooms     → confirm availability filter works
7. Create Booking   → get booking ID + booking_ref
8. Update Payment   → mark as paid (admin)
9. Update Booking   → mark as completed (admin)
10. Post Review     → requires completed booking
11. Add to Wishlist → save room
12. Check Reports   → admin dashboard
```

---

## 1. Auth — `/api/v1/auth/`

### POST `/auth/register/`
Creates a new guest account and returns JWT tokens.

```json
{
  "email": "juan.dela.cruz@email.com",
  "username": "juandc",
  "first_name": "Juan",
  "last_name": "Dela Cruz",
  "phone_number": "09171234567",
  "password": "SecurePass@123",
  "password2": "SecurePass@123"
}
```

**Expected response `201`:**
```json
{
  "user": {
    "id": 1,
    "email": "juan.dela.cruz@email.com",
    "username": "juandc",
    "first_name": "Juan",
    "last_name": "Dela Cruz",
    "phone_number": "09171234567",
    "avatar_url": "",
    "role": "guest",
    "date_joined": "2026-04-25T10:00:00Z",
    "has_password": true,
    "linked_providers": []
  },
  "access": "<access_token>",
  "refresh": "<refresh_token>"
}
```

---

### POST `/auth/login/`
Email/password login. Save the `access` and `refresh` tokens.

```json
{
  "email": "juan.dela.cruz@email.com",
  "password": "SecurePass@123"
}
```

**Admin login** (after running `python manage.py seed_admin`):
```json
{
  "email": "admin@stayease.com",
  "password": "StayEase@2026"
}
```

**Expected response `200`:**
```json
{
  "access": "<access_token>",
  "refresh": "<refresh_token>",
  "user": {
    "id": 2,
    "email": "admin@stayease.com",
    "role": "admin",
    "has_password": true,
    "linked_providers": []
  }
}
```

---

### POST `/auth/token/refresh/`
Get a new access token using your refresh token.

```json
{
  "refresh": "<your_refresh_token>"
}
```

**Expected response `200`:**
```json
{
  "access": "<new_access_token>",
  "refresh": "<new_refresh_token>"
}
```

---

### POST `/auth/logout/`
🔒 Requires auth. Blacklists the refresh token.

```json
{
  "refresh": "<your_refresh_token>"
}
```

**Expected response `200`:**
```json
{
  "detail": "Successfully logged out."
}
```

---

### GET `/auth/me/`
🔒 Requires auth. Returns the current user's profile.

No request body. Add `Authorization: Bearer <token>` header.

**Expected response `200`:**
```json
{
  "id": 1,
  "email": "juan.dela.cruz@email.com",
  "username": "juandc",
  "first_name": "Juan",
  "last_name": "Dela Cruz",
  "phone_number": "09171234567",
  "avatar_url": "",
  "role": "guest",
  "date_joined": "2026-04-25T10:00:00Z",
  "has_password": true,
  "linked_providers": []
}
```

---

### PATCH `/auth/me/`
🔒 Requires auth. Update profile fields (not email or role).

```json
{
  "first_name": "Juan Miguel",
  "phone_number": "09189876543"
}
```

---

### PATCH `/auth/me/avatar/`
🔒 Requires auth. Upload avatar image.  
⚠️ Use `multipart/form-data`, **not** JSON.

```
Content-Type: multipart/form-data

avatar: <image_file.jpg>
```

**Expected response `200`:**
```json
{
  "avatar_url": "https://res.cloudinary.com/your_cloud/image/upload/stayease/avatars/user_1.jpg"
}
```

---

### POST `/auth/oauth/google/`
Sign in with Google. The `id_token` comes from Google Sign-In on your mobile app.

```json
{
  "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6..."
}
```

**Expected response `200` (existing user) or `201` (new user):**
```json
{
  "user": {
    "id": 3,
    "email": "maria@gmail.com",
    "first_name": "Maria",
    "last_name": "Santos",
    "role": "guest",
    "has_password": false,
    "linked_providers": ["google"]
  },
  "access": "<access_token>",
  "refresh": "<refresh_token>"
}
```

---

### POST `/auth/oauth/facebook/`
Sign in with Facebook. The `access_token` comes from Facebook Login on your mobile app.

```json
{
  "access_token": "EAABsbCS1iHgBA..."
}
```

**Expected response `200` or `201`:**
```json
{
  "user": {
    "id": 4,
    "email": "pedro@email.com",
    "first_name": "Pedro",
    "last_name": "Reyes",
    "role": "guest",
    "has_password": false,
    "linked_providers": ["facebook"]
  },
  "access": "<access_token>",
  "refresh": "<refresh_token>"
}
```

---

## 2. Amenities — `/api/v1/amenities/`

> Create these **before** creating rooms so you have real IDs for `amenity_ids`.

### POST `/amenities/`
🔒 Admin only.

```json
{
  "name": "Free Wi-Fi",
  "icon": "wifi"
}
```

Run this for each amenity. Sample set:

```json
{ "name": "Free Wi-Fi", "icon": "wifi" }
{ "name": "Air Conditioning", "icon": "snowflake" }
{ "name": "Flat-screen TV", "icon": "tv" }
{ "name": "Mini Bar", "icon": "glass-martini" }
{ "name": "Bathtub", "icon": "bath" }
{ "name": "City View", "icon": "building" }
{ "name": "Balcony", "icon": "door-open" }
{ "name": "Breakfast Included", "icon": "coffee" }
```

**Expected response `201`:**
```json
{
  "id": 1,
  "name": "Free Wi-Fi",
  "icon": "wifi"
}
```

---

### GET `/amenities/`
Public. No auth required.

**Expected response `200`:**
```json
[
  { "id": 1, "name": "Free Wi-Fi", "icon": "wifi" },
  { "id": 2, "name": "Air Conditioning", "icon": "snowflake" }
]
```

---

## 3. Policies — `/api/v1/policies/`

### POST `/policies/`
🔒 Admin only.

```json
{
  "type": "cancellation",
  "title": "Free Cancellation",
  "description": "Cancel for free up to 48 hours before check-in. Cancellations within 48 hours of check-in are non-refundable."
}
```

More sample policies:

```json
{
  "type": "check-in",
  "title": "Check-in Policy",
  "description": "Check-in time is from 2:00 PM. Early check-in is subject to availability and may incur additional charges."
}
```

```json
{
  "type": "check-out",
  "title": "Check-out Policy",
  "description": "Check-out time is until 12:00 PM noon. Late check-out requests must be made at the front desk."
}
```

```json
{
  "type": "pets",
  "title": "No Pets Allowed",
  "description": "Unfortunately, we do not accommodate pets in any of our rooms or common areas."
}
```

**Expected response `201`:**
```json
{
  "id": 1,
  "type": "cancellation",
  "title": "Free Cancellation",
  "description": "Cancel for free up to 48 hours before check-in. ..."
}
```

---

## 4. Rooms — `/api/v1/rooms/`

### POST `/rooms/`
🔒 Admin only. Use the amenity and policy IDs from steps 2–3.

**Standard Room:**
```json
{
  "name": "Standard Room 101",
  "category": "standard",
  "description": "A comfortable standard room with all essential amenities. Perfect for solo travelers or couples on a budget.",
  "price_per_night": 1500.00,
  "max_guest": 2,
  "availability_status": true,
  "is_featured": false,
  "amenity_ids": [1, 2, 3],
  "policy_ids": [1, 2, 3]
}
```

**Deluxe Room:**
```json
{
  "name": "Deluxe Room 201",
  "category": "deluxe",
  "description": "A spacious deluxe room featuring premium furnishings, a flat-screen TV, and a stunning city view.",
  "price_per_night": 2500.00,
  "max_guest": 2,
  "availability_status": true,
  "is_featured": true,
  "amenity_ids": [1, 2, 3, 4, 6],
  "policy_ids": [1, 2, 3]
}
```

**Junior Suite:**
```json
{
  "name": "Junior Suite 301",
  "category": "junior_suite",
  "description": "A luxurious junior suite with a separate living area, bathtub, and panoramic balcony overlooking the city.",
  "price_per_night": 4500.00,
  "max_guest": 3,
  "availability_status": true,
  "is_featured": true,
  "amenity_ids": [1, 2, 3, 4, 5, 6, 7],
  "policy_ids": [1, 2, 3, 4]
}
```

**Executive Suite:**
```json
{
  "name": "Executive Suite 401",
  "category": "executive_suite",
  "description": "Our premium executive suite offers the finest in luxury accommodation with full butler service, private jacuzzi, and exclusive floor access.",
  "price_per_night": 8500.00,
  "max_guest": 4,
  "availability_status": true,
  "is_featured": true,
  "amenity_ids": [1, 2, 3, 4, 5, 6, 7, 8],
  "policy_ids": [1, 2, 3, 4]
}
```

**Family Room:**
```json
{
  "name": "Family Room 501",
  "category": "family",
  "description": "A generous family room with two queen beds, kid-friendly amenities, and easy access to the hotel pool and play area.",
  "price_per_night": 3800.00,
  "max_guest": 5,
  "availability_status": true,
  "is_featured": false,
  "amenity_ids": [1, 2, 3, 8],
  "policy_ids": [1, 2, 3]
}
```

**Expected response `201`:**
```json
{
  "id": 1,
  "name": "Standard Room 101",
  "category": "standard",
  "category_display": "Standard",
  "description": "A comfortable standard room...",
  "price_per_night": "1500.00",
  "max_guest": 2,
  "rating": "0.00",
  "image_urls": [],
  "availability_status": true,
  "is_featured": false,
  "amenities": [
    { "id": 1, "name": "Free Wi-Fi", "icon": "wifi" },
    { "id": 2, "name": "Air Conditioning", "icon": "snowflake" },
    { "id": 3, "name": "Flat-screen TV", "icon": "tv" }
  ],
  "policies": [
    { "id": 1, "type": "cancellation", "title": "Free Cancellation", "description": "..." }
  ],
  "created_at": "2026-04-25"
}
```

---

### GET `/rooms/`
Public. No auth required.

```
GET /api/v1/rooms/
```

**With filters:**
```
GET /api/v1/rooms/?category=deluxe
GET /api/v1/rooms/?check_in=2026-05-10&check_out=2026-05-15&guests=2
GET /api/v1/rooms/?min_price=2000&max_price=5000
GET /api/v1/rooms/?is_featured=true
GET /api/v1/rooms/?search=suite
GET /api/v1/rooms/?ordering=price_per_night
GET /api/v1/rooms/?ordering=-rating
```

---

### GET `/rooms/featured/`
Public. Returns only `is_featured=true` rooms.

```
GET /api/v1/rooms/featured/
```

---

### GET `/rooms/categories/`
Public. Returns all category choices.

**Expected response `200`:**
```json
[
  { "value": "standard", "label": "Standard" },
  { "value": "deluxe", "label": "Deluxe" },
  { "value": "superior", "label": "Superior" },
  { "value": "junior_suite", "label": "Junior Suite" },
  { "value": "executive_suite", "label": "Executive Suite" },
  { "value": "family", "label": "Family" }
]
```

---

### GET `/rooms/{id}/`
Public. Full room detail with amenities and policies.

```
GET /api/v1/rooms/1/
```

---

### PATCH `/rooms/{id}/`
🔒 Admin only. Update specific fields.

```json
{
  "price_per_night": 1800.00,
  "is_featured": true,
  "availability_status": true
}
```

---

### DELETE `/rooms/{id}/`
🔒 Admin only. No request body needed.

---

### POST `/rooms/{id}/images/`
🔒 Admin only.  
⚠️ Use `multipart/form-data`.

```
Content-Type: multipart/form-data

images: <file1.jpg>
images: <file2.jpg>
```

**Expected response `200`:**
```json
{
  "image_urls": [
    "https://res.cloudinary.com/your_cloud/image/upload/stayease/rooms/1/abc123.jpg",
    "https://res.cloudinary.com/your_cloud/image/upload/stayease/rooms/1/def456.jpg"
  ]
}
```

---

### DELETE `/rooms/{id}/images/remove/`
🔒 Admin only. Remove a specific image URL from the room.

```json
{
  "url": "https://res.cloudinary.com/your_cloud/image/upload/stayease/rooms/1/abc123.jpg"
}
```

---

## 5. Bookings — `/api/v1/bookings/`

### POST `/bookings/create/`
🔒 Guest auth required.

**Single room booking:**
```json
{
  "room_ids": [1],
  "check_in": "2026-05-10",
  "check_out": "2026-05-15",
  "guest_count": 2,
  "payment_method": "gcash"
}
```

**Multi-room booking:**
```json
{
  "room_ids": [2, 3],
  "check_in": "2026-06-01",
  "check_out": "2026-06-05",
  "guest_count": 4,
  "payment_method": "card"
}
```

> Valid `payment_method` values: `card`, `gcash`, `maya`, `cash`

**Expected response `201`:**
```json
{
  "id": 1,
  "booking_ref": "SE-2026-3F9A12B7",
  "check_in": "2026-05-10",
  "check_out": "2026-05-15",
  "nights": 5,
  "guest_count": 2,
  "total_price": "7500.00",
  "status": "pending",
  "is_featured": false,
  "booking_rooms": [
    {
      "id": 1,
      "room": {
        "id": 1,
        "name": "Standard Room 101",
        "category": "standard",
        "price_per_night": "1500.00"
      },
      "price_snapshot": "1500.00"
    }
  ],
  "payment_status": "pending",
  "payment_method": "gcash",
  "created_at": "2026-04-25"
}
```

---

### GET `/bookings/`
🔒 Admin only. Lists all bookings.

```
GET /api/v1/bookings/
GET /api/v1/bookings/?status=pending
GET /api/v1/bookings/?status=confirmed
GET /api/v1/bookings/?search=SE-2026
```

---

### GET `/bookings/my/`
🔒 Guest auth. Returns the logged-in user's bookings.

```
GET /api/v1/bookings/my/
```

---

### GET `/bookings/{id}/`
🔒 Owner or admin. Full booking detail.

```
GET /api/v1/bookings/1/
```

---

### PATCH `/bookings/{id}/status/`
🔒 Admin only. Update booking status.

**Confirm a booking:**
```json
{
  "status": "confirmed"
}
```

**Mark as completed** (required before guest can post a review):
```json
{
  "status": "completed"
}
```

**Cancel a booking:**
```json
{
  "status": "cancelled"
}
```

> Valid values: `confirmed`, `cancelled`, `completed`

---

### POST `/bookings/{id}/cancel/`
🔒 Guest auth. Guest self-cancels their own pending/confirmed booking.

No request body needed.

**Expected response `200`:**
```json
{
  "detail": "Booking cancelled.",
  "booking_ref": "SE-2026-3F9A12B7"
}
```

---

## 6. Payments — `/api/v1/payments/`

### GET `/payments/{booking_id}/`
🔒 Owner or admin. Get payment details for a booking.

```
GET /api/v1/payments/1/
```

**Expected response `200`:**
```json
{
  "id": 1,
  "booking_ref": "SE-2026-3F9A12B7",
  "amount": "7500.00",
  "method": "gcash",
  "status": "pending",
  "transaction_ref": "",
  "paid_at": null
}
```

---

### PATCH `/payments/{booking_id}/update/`
🔒 Admin only. Manually update payment status (simulated gateway).

**Mark as paid:**
```json
{
  "status": "paid",
  "transaction_ref": "GCH-20260425-00123",
  "paid_at": "2026-04-25T14:30:00Z"
}
```

**Mark as refunded:**
```json
{
  "status": "refunded",
  "transaction_ref": "REF-20260425-00456",
  "paid_at": null
}
```

> Valid `status` values: `pending`, `paid`, `failed`, `refunded`

---

## 7. Reviews — `/api/v1/reviews/`

> ⚠️ The booking must have `status: completed` before a review can be posted.

### POST `/reviews/`
🔒 Guest auth. Submit a review for a room in a completed booking.

```json
{
  "room": 1,
  "booking": 1,
  "rating": 5,
  "comment": "Absolutely wonderful stay! The room was spotless, the staff were very accommodating, and the view was breathtaking. Will definitely come back."
}
```

**Rating 4 — minor issue:**
```json
{
  "room": 2,
  "booking": 2,
  "rating": 4,
  "comment": "Great room overall. The amenities were excellent but the Wi-Fi was a bit slow in the evening. Everything else was perfect."
}
```

**Rating 3 — average:**
```json
{
  "room": 3,
  "booking": 3,
  "rating": 3,
  "comment": "Decent room for the price. Nothing exceptional but nothing bad either. The location is very convenient."
}
```

> Valid `rating` values: `1` to `5`

**Expected response `201`:**
```json
{
  "id": 1,
  "user_name": "Juan Dela Cruz",
  "room": 1,
  "room_name": "Standard Room 101",
  "booking": 1,
  "rating": 5,
  "comment": "Absolutely wonderful stay!...",
  "created_at": "2026-04-25"
}
```

---

### GET `/reviews/`
Public. List all reviews. Filter by room.

```
GET /api/v1/reviews/
GET /api/v1/reviews/?room=1
GET /api/v1/reviews/?ordering=-rating
GET /api/v1/reviews/?ordering=-created_at
```

---

### PATCH `/reviews/{id}/`
🔒 Owner only. Edit your own review.

```json
{
  "rating": 4,
  "comment": "Updated review: Great stay overall, but the breakfast service was a bit slow on the last day."
}
```

---

### DELETE `/reviews/{id}/`
🔒 Owner only. No request body needed.

---

## 8. Wishlist — `/api/v1/wishlist/`

### POST `/wishlist/`
🔒 Guest auth. Add a room to wishlist.

```json
{
  "room_id": 3
}
```

**Expected response `201`:**
```json
{
  "id": 1,
  "room": {
    "id": 3,
    "name": "Junior Suite 301",
    "category": "junior_suite",
    "price_per_night": "4500.00",
    "max_guest": 3,
    "rating": "0.00",
    "image_urls": [],
    "availability_status": true,
    "is_featured": true
  },
  "created_at": "2026-04-25"
}
```

---

### GET `/wishlist/`
🔒 Guest auth. Get your saved rooms.

```
GET /api/v1/wishlist/
```

---

### DELETE `/wishlist/{room_id}/`
🔒 Guest auth. Remove room from wishlist. No request body.

```
DELETE /api/v1/wishlist/3/
```

**Expected response `204`:** No content.

---

## 9. Reports — `/api/v1/reports/`

> 🔒 All report endpoints are Admin only.

### GET `/reports/dashboard/`
Summary cards for the admin home screen.

```
GET /api/v1/reports/dashboard/
```

**Expected response `200`:**
```json
{
  "bookings": {
    "total": 24,
    "pending": 5,
    "confirmed": 12,
    "cancelled": 7
  },
  "revenue": {
    "total": 187500.00,
    "this_month": 45000.00
  },
  "rooms": {
    "total": 10,
    "available": 8
  },
  "today": {
    "check_ins": 3,
    "check_outs": 2
  }
}
```

---

### GET `/reports/revenue/`
Revenue grouped by period.

```
GET /api/v1/reports/revenue/?period=monthly
GET /api/v1/reports/revenue/?period=monthly&year=2026
GET /api/v1/reports/revenue/?period=weekly&year=2026
GET /api/v1/reports/revenue/?period=daily&year=2026&month=4
```

> Valid `period` values: `daily`, `weekly`, `monthly`

**Expected response `200`:**
```json
{
  "period": "monthly",
  "results": [
    {
      "period": "2026-03-01",
      "total_revenue": 87500.00,
      "booking_count": 12
    },
    {
      "period": "2026-04-01",
      "total_revenue": 45000.00,
      "booking_count": 7
    }
  ]
}
```

---

### GET `/reports/occupancy/`
Occupancy rate per room category.

```
GET /api/v1/reports/occupancy/?period=monthly
GET /api/v1/reports/occupancy/?period=weekly
GET /api/v1/reports/occupancy/?period=daily
```

**Expected response `200`:**
```json
{
  "period": "monthly",
  "results": [
    {
      "category": "standard",
      "category_display": "Standard",
      "total_rooms": 3,
      "booked_rooms": 2,
      "occupancy_rate": 66.67
    },
    {
      "category": "deluxe",
      "category_display": "Deluxe",
      "total_rooms": 2,
      "booked_rooms": 2,
      "occupancy_rate": 100.0
    },
    {
      "category": "junior_suite",
      "category_display": "Junior Suite",
      "total_rooms": 2,
      "booked_rooms": 1,
      "occupancy_rate": 50.0
    }
  ]
}
```

---

### GET `/reports/top-rooms/`
Top performing rooms by revenue or booking count.

```
GET /api/v1/reports/top-rooms/
GET /api/v1/reports/top-rooms/?order_by=revenue&limit=5
GET /api/v1/reports/top-rooms/?order_by=bookings&limit=10
```

> Valid `order_by` values: `revenue`, `bookings`  
> `limit`: 1–50 (default: 10)

**Expected response `200`:**
```json
{
  "order_by": "revenue",
  "results": [
    {
      "room_id": 4,
      "room_name": "Executive Suite 401",
      "category": "executive_suite",
      "total_revenue": 85000.00,
      "booking_count": 10
    },
    {
      "room_id": 3,
      "room_name": "Junior Suite 301",
      "category": "junior_suite",
      "total_revenue": 45000.00,
      "booking_count": 10
    },
    {
      "room_id": 2,
      "room_name": "Deluxe Room 201",
      "category": "deluxe",
      "total_revenue": 25000.00,
      "booking_count": 10
    }
  ]
}
```

---

## Common Error Responses

### `400 Bad Request` — Validation error
```json
{
  "check_out": ["Check-out must be after check-in."],
  "room_ids": ["One or more rooms are unavailable or do not exist."]
}
```

### `401 Unauthorized` — Missing or expired token
```json
{
  "detail": "Authentication credentials were not provided."
}
```

```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid"
}
```

### `403 Forbidden` — Insufficient role
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### `404 Not Found`
```json
{
  "detail": "Not found."
}
```

---

## Quick Postman Setup

1. Create a **collection** called `StayEase`
2. Add a **collection variable** `base_url = http://127.0.0.1:8000/api/v1`
3. After login, copy the `access` token into a variable `access_token`
4. Set the collection **Authorization** to `Bearer {{access_token}}`
5. For admin-only endpoints, repeat with a separate `admin_token` variable
