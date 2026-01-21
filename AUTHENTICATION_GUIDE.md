# Restaurant Reservation System - Authentication & User Management Guide

## 📋 Table of Contents
- [Overview](#overview)
- [Features Implemented](#features-implemented)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [Security Features](#security-features)
- [Setup & Configuration](#setup--configuration)
- [Usage Examples](#usage-examples)
- [RBAC (Role-Based Access Control)](#rbac-role-based-access-control)
- [Frontend Integration](#frontend-integration)

---

## 🎯 Overview

This authentication system implements a secure, production-ready user management module with email verification, password reset, role-based access control, and protection against common attacks.

### Technology Stack
- **Backend**: FastAPI + Python
- **Database**: MySQL with SQLAlchemy ORM
- **Authentication**: JWT (Access + Refresh tokens)
- **Password Hashing**: bcrypt (via passlib)
- **Email**: SMTP (configurable)

---

## ✨ Features Implemented

### 1. User Registration
- ✅ Email and password registration
- ✅ Optional phone number field
- ✅ Role selection (Customer, Restaurant Owner, Admin)
- ✅ Strong password validation:
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one number
- ✅ Email verification workflow
- ✅ Duplicate email prevention
- ✅ Rate limiting (5 requests/minute)

### 2. Email Verification
- ✅ Secure verification tokens (single-use)
- ✅ 24-hour token expiration
- ✅ Automatic verification emails
- ✅ Users must verify before login

### 3. User Login
- ✅ Email + password authentication
- ✅ Email verification check
- ✅ Brute force protection:
  - Account lockout after 5 failed attempts
  - 15-minute lockout duration
  - Automatic unlock after timeout
- ✅ JWT token generation (access + refresh)
- ✅ Rate limiting (5 requests/minute)

### 4. Password Reset
- ✅ Forgot password endpoint
- ✅ Secure reset tokens (single-use)
- ✅ 1-hour token expiration
- ✅ Password reset emails
- ✅ Email enumeration prevention
- ✅ Rate limiting (3 requests/minute)
- ✅ All sessions invalidated on password change

### 5. Token Management
- ✅ Access tokens (15-minute expiry)
- ✅ Refresh tokens (30-day expiry)
- ✅ Token refresh endpoint
- ✅ Token revocation (logout)
- ✅ Logout from all devices
- ✅ Automatic token cleanup

### 6. Role-Based Access Control (RBAC)
- ✅ Three user roles:
  - **Customer** (role=0): Basic user, can make reservations
  - **Restaurant Owner** (role=1): Can manage restaurants
  - **Admin** (role=2): Full system access
- ✅ Role-based authorization middleware
- ✅ Reusable permission dependencies

### 7. Security Features
- ✅ Password hashing with bcrypt
- ✅ Rate limiting on auth endpoints
- ✅ Brute force protection
- ✅ Token blacklisting (refresh tokens in DB)
- ✅ Single-use tokens for verification/reset
- ✅ Email enumeration prevention
- ✅ CORS configuration
- ✅ Input validation with Pydantic

---

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    role INT NOT NULL DEFAULT 0,
    first_name VARCHAR(15) NOT NULL,
    last_name VARCHAR(15) NOT NULL,
    user_email VARCHAR(40) NOT NULL UNIQUE,
    user_password VARCHAR(80) NOT NULL,
    phone_number VARCHAR(20),
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    failed_login_attempts INT NOT NULL DEFAULT 0,
    locked_until DATETIME,
    registered_at DATETIME NOT NULL,
    edited_at DATETIME,
    INDEX idx_first_name (first_name),
    INDEX idx_last_name (last_name),
    INDEX idx_user_email (user_email)
);
```

### Refresh Tokens Table
```sql
CREATE TABLE refresh_tokens (
    id INT PRIMARY KEY AUTO_INCREMENT,
    token VARCHAR(255) NOT NULL UNIQUE,
    user_id INT NOT NULL,
    expires_at DATETIME NOT NULL,
    status VARCHAR(20) NOT NULL,  -- ACTIVE, REVOKED, EXPIRED
    created_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_token (token)
);
```

### Password Reset Tokens Table
```sql
CREATE TABLE password_reset_tokens (
    id INT PRIMARY KEY AUTO_INCREMENT,
    token VARCHAR(255) NOT NULL UNIQUE,
    user_id INT NOT NULL,
    expires_at DATETIME NOT NULL,
    is_used BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL,
    used_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_token (token)
);
```

---

## 🌐 API Endpoints

### Base URL: `http://localhost:8000/api/authentication`

### 1. Register User
**POST** `/register`

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "user_email": "john@example.com",
  "user_password": "SecurePass123",
  "phone_number": "+1234567890",
  "role": 0
}
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number

**Response:** (200 OK)
```json
{
  "message": "Registration successful. Please check your email to verify your account.",
  "email": "john@example.com"
}
```

---

### 2. Verify Email
**POST** `/verify-email`

**Request Body:**
```json
{
  "token": "secure-verification-token-from-email"
}
```

**Response:** (200 OK)
```json
{
  "message": "Email verified successfully. You can now log in.",
  "email": "john@example.com"
}
```

---

### 3. Login
**POST** `/login`

**Request Body:**
```json
{
  "user_email": "john@example.com",
  "user_password": "SecurePass123"
}
```

**Response:** (200 OK)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses:**
- `400`: Invalid email or password
- `403`: Email not verified
- `423`: Account locked (too many failed attempts)
- `429`: Too many requests (rate limited)

---

### 4. Refresh Token
**POST** `/refresh`

**Request Body:**
```json
{
  "refresh_token": "your-refresh-token"
}
```

**Response:** (200 OK)
```json
{
  "access_token": "new-access-token",
  "refresh_token": "new-refresh-token",
  "token_type": "bearer"
}
```

---

### 5. Get Current User
**GET** `/me`

**Headers:**
```
Authorization: Bearer <access-token>
```

**Response:** (200 OK)
```json
{
  "id": 1,
  "first_name": "John",
  "last_name": "Doe",
  "user_email": "john@example.com",
  "phone_number": "+1234567890",
  "role": 0,
  "email_verified": true
}
```

---

### 6. Logout (Single Device)
**POST** `/logout`

**Request Body:**
```json
{
  "refresh_token": "your-refresh-token"
}
```

**Response:** (200 OK)
```json
{
  "message": "Successfully logged out"
}
```

---

### 7. Logout (All Devices)
**POST** `/logout-all`

**Request Body:**
```json
{
  "refresh_token": "your-refresh-token"
}
```

**Response:** (200 OK)
```json
{
  "message": "Successfully logged out from all devices"
}
```

---

### 8. Forgot Password
**POST** `/forgot-password`

**Request Body:**
```json
{
  "user_email": "john@example.com"
}
```

**Response:** (200 OK)
```json
{
  "message": "If an account exists with this email, a password reset link has been sent."
}
```

**Note:** Always returns success to prevent email enumeration attacks.

---

### 9. Reset Password
**POST** `/reset-password`

**Request Body:**
```json
{
  "token": "reset-token-from-email",
  "new_password": "NewSecurePass456"
}
```

**Response:** (200 OK)
```json
{
  "message": "Password reset successfully. You can now log in with your new password."
}
```

**Note:** All existing sessions are invalidated on password reset.

---

## 🔒 Security Features

### 1. Password Security
- **Hashing**: bcrypt with automatic salt generation
- **Strength Requirements**: 8+ chars, uppercase, lowercase, number
- **Storage**: Never stored in plaintext

### 2. Token Security
- **Access Tokens**: Short-lived (15 min), stored in memory/localStorage
- **Refresh Tokens**: Long-lived (30 days), stored in database for revocation
- **Single-use**: Verification and reset tokens can only be used once
- **Expiration**: All tokens have expiration timestamps
- **Revocation**: Refresh tokens can be revoked on logout or password change

### 3. Brute Force Protection
- **Failed Login Tracking**: Counter increments on failed attempts
- **Account Lockout**: After 5 failed attempts
- **Lockout Duration**: 15 minutes
- **Automatic Reset**: Counter resets on successful login
- **Automatic Unlock**: Account unlocks after timeout expires

### 4. Rate Limiting
- **Authentication Endpoints**: 5 requests/minute
- **Password Reset**: 3 requests/minute (stricter)
- **Implementation**: In-memory rate limiter with IP tracking
- **Response**: HTTP 429 Too Many Requests

### 5. Email Security
- **Enumeration Prevention**: Forgot password always returns success
- **Secure Tokens**: 32-byte URL-safe tokens using `secrets` module
- **Token Expiration**:
  - Email verification: 24 hours
  - Password reset: 1 hour
- **Single-use Tokens**: Marked as used after redemption

### 6. Additional Protections
- **CORS**: Configured for frontend origin
- **Input Validation**: Pydantic schemas validate all inputs
- **SQL Injection**: SQLAlchemy ORM prevents SQL injection
- **XSS**: FastAPI auto-escapes output

---

## ⚙️ Setup & Configuration

### 1. Database Migration

Run the migration to create the new tables and fields:

```bash
cd backend
py -m alembic upgrade head
```

### 2. Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Database
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/rr

# JWT Secret (generate a secure random string)
SECRET_KEY=your-secret-key-here

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourapp.com

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

### 3. Gmail SMTP Setup

If using Gmail for sending emails:

1. Enable 2-Factor Authentication on your Google account
2. Go to Google Account Settings → Security
3. Under "2-Step Verification", click "App passwords"
4. Generate an app password for "Mail"
5. Use this app password (not your regular password) in `SMTP_PASSWORD`

### 4. Test Email Configuration

The email service will log errors if SMTP credentials are incorrect. Check the backend logs when testing registration or password reset.

---

## 📝 Usage Examples

### Example 1: Register and Verify Email

```python
import requests

# 1. Register user
response = requests.post("http://localhost:8000/api/authentication/register", json={
    "first_name": "Jane",
    "last_name": "Smith",
    "user_email": "jane@example.com",
    "user_password": "SecurePass123",
    "phone_number": "+1234567890",
    "role": 0  # Customer
})
print(response.json())
# {"message": "Registration successful. Please check your email..."}

# 2. Check email for verification link
# Link format: http://localhost:3000/verify-email?token=abc123...

# 3. Verify email
response = requests.post("http://localhost:8000/api/authentication/verify-email", json={
    "token": "abc123..."
})
print(response.json())
# {"message": "Email verified successfully..."}
```

### Example 2: Login and Access Protected Route

```python
# 1. Login
response = requests.post("http://localhost:8000/api/authentication/login", json={
    "user_email": "jane@example.com",
    "user_password": "SecurePass123"
})
tokens = response.json()

# 2. Access protected route
headers = {"Authorization": f"Bearer {tokens['access_token']}"}
response = requests.get("http://localhost:8000/api/authentication/me", headers=headers)
print(response.json())
# {"id": 1, "first_name": "Jane", ...}
```

### Example 3: Password Reset Flow

```python
# 1. Request password reset
response = requests.post("http://localhost:8000/api/authentication/forgot-password", json={
    "user_email": "jane@example.com"
})
# Always returns success (prevents email enumeration)

# 2. Check email for reset link
# Link format: http://localhost:3000/reset-password?token=xyz789...

# 3. Reset password
response = requests.post("http://localhost:8000/api/authentication/reset-password", json={
    "token": "xyz789...",
    "new_password": "NewSecurePass456"
})
print(response.json())
# {"message": "Password reset successfully..."}
```

---

## 👥 RBAC (Role-Based Access Control)

### User Roles

| Role | Value | Description | Permissions |
|------|-------|-------------|-------------|
| Customer | 0 | Default role | Search restaurants, make reservations |
| Restaurant Owner | 1 | Business users | Manage restaurant profile, view reservations |
| Admin | 2 | System administrators | Full system access, user management |

### Using RBAC in Endpoints

The system provides reusable dependencies for protecting endpoints:

```python
from fastapi import APIRouter, Depends
from app.utils.rbac import (
    get_current_user,
    require_admin,
    require_restaurant_owner,
    require_customer,
    require_restaurant_owner_or_admin,
    require_roles
)
from app.models.user import User, UserRole

router = APIRouter()

# Example 1: Get current authenticated user
@router.get("/profile")
def get_profile(current_user: User = Depends(get_current_user)):
    return {"email": current_user.user_email, "role": current_user.role}

# Example 2: Admin-only endpoint
@router.get("/admin/users", dependencies=[Depends(require_admin)])
def list_users():
    return {"users": [...]}

# Example 3: Restaurant owner only
@router.post("/restaurant", dependencies=[Depends(require_restaurant_owner)])
def create_restaurant():
    return {"message": "Restaurant created"}

# Example 4: Multiple roles allowed
@router.get("/dashboard", dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.RESTAURANT_OWNER]))])
def dashboard():
    return {"data": "..."}

# Example 5: Access current user in handler
@router.get("/my-reservations")
def my_reservations(current_user: User = Depends(get_current_user)):
    # current_user is the authenticated User object
    return {"user_id": current_user.id, "reservations": [...]}
```

### Response Codes
- **401 Unauthorized**: Missing or invalid token
- **403 Forbidden**: Valid token but insufficient permissions

---

## 🎨 Frontend Integration

### Required Frontend Pages

You need to create these pages in your React frontend:

1. **Email Verification Page** (`/verify-email`)
   - Extract token from URL query params
   - Call `/verify-email` endpoint
   - Show success/error message
   - Redirect to login

2. **Password Reset Page** (`/reset-password`)
   - Extract token from URL query params
   - Show password reset form
   - Call `/reset-password` endpoint
   - Redirect to login on success

3. **Forgot Password Page** (`/forgot-password`)
   - Show email input form
   - Call `/forgot-password` endpoint
   - Show instructions message

### Example: Email Verification Page

```tsx
// src/pages/Auth/VerifyEmailPage.tsx
import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');

  useEffect(() => {
    const token = searchParams.get('token');
    if (!token) {
      setStatus('error');
      setMessage('Invalid verification link');
      return;
    }

    fetch('http://localhost:8000/api/authentication/verify-email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token })
    })
      .then(res => res.json())
      .then(data => {
        setStatus('success');
        setMessage(data.message);
        setTimeout(() => navigate('/login'), 3000);
      })
      .catch(err => {
        setStatus('error');
        setMessage('Verification failed. Token may be expired.');
      });
  }, [searchParams, navigate]);

  return (
    <div className="verify-email-page">
      {status === 'loading' && <p>Verifying your email...</p>}
      {status === 'success' && (
        <div>
          <h2>✓ Email Verified!</h2>
          <p>{message}</p>
          <p>Redirecting to login...</p>
        </div>
      )}
      {status === 'error' && (
        <div>
          <h2>✗ Verification Failed</h2>
          <p>{message}</p>
        </div>
      )}
    </div>
  );
}
```

### Update Registration Form

Add phone number and role selection fields:

```tsx
// Update src/pages/Auth/RegisterPage.tsx
const [formData, setFormData] = useState({
  first_name: '',
  last_name: '',
  user_email: '',
  user_password: '',
  phone_number: '',
  role: 0 // 0=Customer, 1=Restaurant Owner, 2=Admin
});

// Add to form JSX:
<input
  type="tel"
  placeholder="Phone Number"
  value={formData.phone_number}
  onChange={(e) => setFormData({...formData, phone_number: e.target.value})}
/>

<select
  value={formData.role}
  onChange={(e) => setFormData({...formData, role: Number(e.target.value)})}
>
  <option value={0}>Customer</option>
  <option value={1}>Restaurant Owner</option>
</select>
```

---

## 🧪 Testing

### Manual Testing Checklist

#### Registration & Email Verification
- [ ] Register with weak password → Should fail with validation error
- [ ] Register with valid data → Should succeed, send email
- [ ] Try to login before verification → Should fail with "Email not verified"
- [ ] Verify email with token → Should succeed
- [ ] Try to verify again with same token → Should fail (single-use)
- [ ] Login after verification → Should succeed

#### Login & Brute Force Protection
- [ ] Login with wrong password 3 times → Should still allow attempts
- [ ] Login with wrong password 5 times → Account should lock
- [ ] Try to login while locked → Should show lockout message
- [ ] Wait 15 minutes → Account should auto-unlock
- [ ] Login with correct password → Should succeed and reset counter

#### Password Reset
- [ ] Request password reset → Should send email
- [ ] Use reset token to change password → Should succeed
- [ ] Try to use same token again → Should fail (single-use)
- [ ] Try to login with old password → Should fail
- [ ] Login with new password → Should succeed

#### Rate Limiting
- [ ] Make 6 requests to /login rapidly → 6th should be rate limited (429)
- [ ] Make 4 requests to /forgot-password rapidly → 4th should be rate limited (429)
- [ ] Wait 1 minute → Should be able to make requests again

#### RBAC
- [ ] Login as Customer → Should not access admin endpoints (403)
- [ ] Login as Admin → Should access all endpoints
- [ ] Access protected route without token → Should fail (401)

---

## 📚 File Structure

```
backend/
├── app/
│   ├── models/
│   │   ├── user.py                        # User model with UserRole enum
│   │   ├── refresh_token.py               # RefreshToken model
│   │   └── password_reset_token.py        # PasswordResetToken model
│   ├── schemas/
│   │   ├── user_schema.py                 # User schemas with validation
│   │   └── token_schema.py                # Token schemas
│   ├── controllers/
│   │   └── authentication_controller.py   # All auth endpoints
│   ├── utils/
│   │   ├── jwt_utils.py                   # JWT token utilities
│   │   ├── email_service.py               # Email sending service
│   │   ├── rbac.py                        # Role-based access control
│   │   └── rate_limiter.py                # Rate limiting middleware
│   └── db/
│       ├── migrations/                    # Alembic migrations
│       └── database.py                    # Database config
├── .env                                   # Environment variables
├── .env.example                           # Example env file
└── requirements.txt                       # Python dependencies

frontend/
├── src/
│   ├── pages/
│   │   └── Auth/
│   │       ├── LoginPage.tsx             # Login form
│   │       ├── RegisterPage.tsx          # Registration form
│   │       ├── VerifyEmailPage.tsx       # Email verification (NEW)
│   │       ├── ForgotPasswordPage.tsx    # Forgot password (NEW)
│   │       └── ResetPasswordPage.tsx     # Password reset (NEW)
│   └── context/
│       └── AuthContext.tsx               # Auth state management
```

---

## 🚀 Next Steps

1. **Run Database Migration**
   ```bash
   cd backend
   py -m alembic revision --autogenerate -m "add_user_security_fields"
   py -m alembic upgrade head
   ```

2. **Configure Email**
   - Update `.env` with SMTP credentials
   - Test by registering a new user

3. **Update Frontend**
   - Create email verification page
   - Create password reset pages
   - Update registration form (add phone number and role selection)

4. **Test the System**
   - Follow the testing checklist above
   - Verify all security features work correctly

5. **Production Deployment**
   - Use HTTPS in production
   - Update `FRONTEND_URL` to production URL
   - Use environment-specific SMTP credentials
   - Consider using a professional email service (SendGrid, AWS SES, etc.)

---

## 🆘 Troubleshooting

### Email Not Sending
- Check SMTP credentials in `.env`
- For Gmail: Ensure you're using an App Password, not your regular password
- Check backend logs for error messages
- Test SMTP connection separately

### Account Locked
- Wait 15 minutes for automatic unlock
- Or manually reset in database:
  ```sql
  UPDATE users SET failed_login_attempts = 0, locked_until = NULL WHERE user_email = 'user@example.com';
  ```

### Token Expired
- Email verification tokens: 24 hours
- Password reset tokens: 1 hour
- Request a new token if expired

### Rate Limited
- Wait 1 minute before retrying
- Check if you're making requests too quickly
- Consider increasing limits in production

---

## 📞 Support

For issues or questions:
1. Check this documentation
2. Review backend logs for error messages
3. Test with Postman/curl to isolate frontend vs backend issues
4. Check database state for debugging

---

**Created**: January 2026
**Version**: 1.0
**System**: Restaurant Reservation Platform
