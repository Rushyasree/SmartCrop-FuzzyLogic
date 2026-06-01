# 🚀 CROP ZEN PHASE 2 - QUICK REFERENCE

## 📋 Quick Start (5 minutes)

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Create PostgreSQL database
createdb -U postgres crop_zen

# 3. Setup Alembic migrations
python setup_alembic.py

# 4. Start Flask server
python app.py

# Server running at http://localhost:5000
```

---

## 🔐 Authentication Flow

### Register User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "farmer@example.com",
    "password": "SecurePass123",
    "first_name": "John",
    "last_name": "Farmer",
    "phone": "9876543210"
  }'
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "Bearer",
    "user": {
      "id": 1,
      "email": "farmer@example.com",
      "first_name": "John",
      "last_name": "Farmer"
    }
  }
}
```

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "farmer@example.com",
    "password": "SecurePass123"
  }'
```

### Refresh Token
```bash
curl -X POST http://localhost:5000/api/auth/refresh-token \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "YOUR_REFRESH_TOKEN"}'
```

### Get Current User
```bash
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🌾 Farm Management

### List Farms
```bash
curl -X GET http://localhost:5000/api/farms \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Create Farm
```bash
curl -X POST http://localhost:5000/api/farms \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "North Farm",
    "location": "Village XYZ",
    "state": "MH",
    "district": "Pune",
    "size_hectares": 15.5,
    "soil_type": "black",
    "latitude": 18.5204,
    "longitude": 73.8567
  }'
```

### Get Farm Details
```bash
curl -X GET http://localhost:5000/api/farms/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Update Farm
```bash
curl -X PUT http://localhost:5000/api/farms/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "size_hectares": 20.0,
    "soil_type": "red"
  }'
```

### Delete Farm
```bash
curl -X DELETE http://localhost:5000/api/farms/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📊 Predictions & Data

### Store Prediction
```bash
curl -X POST http://localhost:5000/api/predictions \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "farm_id": 1,
    "crop_name": "Rice",
    "soil_ph": 6.5,
    "moisture": 65.0,
    "temperature": 28.5,
    "rainfall": 120.0,
    "confidence_score": 0.92,
    "season": "KHARIF"
  }'
```

### List Predictions (with pagination)
```bash
# Get first page (10 per page)
curl -X GET "http://localhost:5000/api/predictions?page=1&per_page=10" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get second page
curl -X GET "http://localhost:5000/api/predictions?page=2&per_page=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🗄️ Database Schemas

### Users Table
```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  phone VARCHAR(20),
  role ENUM('farmer', 'admin', 'researcher'),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

### Farms Table
```sql
CREATE TABLE farms (
  id INTEGER PRIMARY KEY,
  owner_id INTEGER FOREIGN KEY REFERENCES users(id),
  name VARCHAR(100) NOT NULL,
  location VARCHAR(255),
  state VARCHAR(50),
  district VARCHAR(100),
  size_hectares FLOAT,
  soil_type VARCHAR(50),
  latitude FLOAT,
  longitude FLOAT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

### Predictions Table
```sql
CREATE TABLE predictions (
  id INTEGER PRIMARY KEY,
  farm_id INTEGER FOREIGN KEY REFERENCES farms(id),
  crop_name VARCHAR(100),
  soil_ph FLOAT,
  moisture FLOAT,
  temperature FLOAT,
  rainfall FLOAT,
  confidence_score FLOAT,
  season ENUM('kharif', 'rabi', 'summer', 'year_round'),
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

---

## 🧪 Running Tests

```bash
# Run all Phase 2 tests
pytest test_phase2.py -v

# Run specific test class
pytest test_phase2.py::TestAuthentication -v

# Run with coverage report
pytest test_phase2.py --cov=. --cov-report=html

# Run only authentication tests with details
pytest test_phase2.py::TestAuthentication -vv
```

---

## ⚙️ Environment Variables

```env
# .env file
DATABASE_URL=postgresql://postgres:password@localhost:5432/crop_zen
SECRET_KEY=your-secret-key-change-in-production
FLASK_ENV=development
FLASK_DEBUG=True
FRONTEND_URL=http://localhost:3000
```

---

## 🔍 Common Errors & Solutions

### "Connection refused" to PostgreSQL
```bash
# Start PostgreSQL
# Windows: Use Services or pgAdmin
# Mac: brew services start postgresql
# Linux: sudo systemctl start postgresql

# Verify it's running
psql -U postgres -d crop_zen -c "SELECT 1;"
```

### "ModuleNotFoundError"
```bash
# Install dependencies
pip install -r requirements.txt

# Verify you're in virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate      # Windows
```

### Alembic Issues
```bash
# Reset migrations
rm -rf alembic
python setup_alembic.py
```

### CORS Errors
```python
# Update CORS in app.py for your frontend URL
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"],  # Your frontend URL
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

---

## 📁 Project Structure

```
backend/
├── app.py                         # Flask application
├── auth.py                        # Password & JWT functions
├── auth_routes.py                 # Authentication endpoints
├── database.py                    # SQLAlchemy config
├── data_routes.py                 # Farm & prediction endpoints
├── models.py                      # ORM models (User, Farm, etc)
├── services/legacy_rule_fallback.py # Legacy pH/moisture crop fallback
├── disease_model.py               # Disease detection logic
├── setup_alembic.py               # Migration automation
├── test_phase2.py                 # Test suite
├── requirements.txt               # Dependencies
├── .env                           # Environment variables (dev)
├── .env.example                   # Configuration template
├── PHASE2_SETUP.md                # Setup guide
├── PHASE2_IMPLEMENTATION.md       # Technical docs
├── PHASE2_COMPLETION_REPORT.md    # Session report
└── logs/
    └── crop_zen.log               # Application logs
```

---

## 🔐 Security Checklist

Before deploying to production:

- [ ] Change SECRET_KEY to strong random value
- [ ] Update DATABASE_URL with production credentials
- [ ] Set FLASK_ENV=production
- [ ] Set FLASK_DEBUG=False
- [ ] Update CORS origins to match frontend domain
- [ ] Enable HTTPS/SSL
- [ ] Set up database backups
- [ ] Configure firewall rules
- [ ] Use Gunicorn (not Flask debug mode)
- [ ] Implement rate limiting
- [ ] Set up monitoring and logging
- [ ] Enable security headers

---

## 📊 API Endpoints Summary

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/auth/register` | POST | No | Register new user |
| `/api/auth/login` | POST | No | Login user |
| `/api/auth/refresh-token` | POST | No | Refresh access token |
| `/api/auth/me` | GET | Yes | Get current user |
| `/api/farms` | GET | Yes | List farms |
| `/api/farms` | POST | Yes | Create farm |
| `/api/farms/{id}` | GET | Yes | Get farm |
| `/api/farms/{id}` | PUT | Yes | Update farm |
| `/api/farms/{id}` | DELETE | Yes | Delete farm |
| `/api/predictions` | GET | Yes | List predictions |
| `/api/predictions` | POST | Yes | Store prediction |
| `/api/predict` | POST | No | Crop prediction (legacy) |
| `/api/crops` | GET | No | List crops |
| `/health` | GET | No | Health check |

---

## 🎯 Token Authorization Header

All authenticated endpoints require:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Example:**
```bash
curl -X GET http://localhost:5000/api/farms \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20iLCJleHAiOjE2Mjc0OTI5OTl9.xY..."
```

---

## 📝 Useful Commands

```bash
# View logs
tail -f logs/crop_zen.log

# Test database connection
python -c "from database import test_connection; test_connection()"

# Run a Python shell with models loaded
python
>>> from models import User, Farm
>>> from database import SessionLocal
>>> db = SessionLocal()
>>> users = db.query(User).all()

# Create initial admin user (manually)
python
>>> from database import SessionLocal
>>> from models import User, UserRole
>>> from auth import hash_password
>>> db = SessionLocal()
>>> admin = User(email="admin@example.com", password_hash=hash_password("AdminPass123"), role=UserRole.ADMIN)
>>> db.add(admin)
>>> db.commit()

# Generate strong SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🚀 Deployment Commands

```bash
# Using Gunicorn (production)
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# With environment file
gunicorn -w 4 -b 0.0.0.0:5000 --env FLASK_ENV=production app:app

# Development (debug mode)
python app.py

# Using Flask CLI
export FLASK_APP=app.py
flask run
```

---

## 📚 Further Reading

- `PHASE2_SETUP.md` - Complete setup guide
- `PHASE2_IMPLEMENTATION.md` - Technical architecture
- `PHASE2_COMPLETION_REPORT.md` - Session summary
- `API_DOCUMENTATION.md` - Full API reference
- Inline docstrings in Python files

---

## 🤝 Contributing

When adding new features:
1. Follow existing code style (PEP-8)
2. Add type hints to functions
3. Write comprehensive docstrings
4. Add test cases in `test_phase2.py`
5. Update documentation
6. Ensure >85% test coverage

---

## 📞 Support

For issues:
1. Check troubleshooting section in this guide
2. Review `PHASE2_SETUP.md`
3. Check application logs
4. Review inline code comments

---

**Last Updated**: May 27, 2024  
**Version**: Phase 2 Backend v1.0  
**Status**: ✅ Production Ready for Testing
