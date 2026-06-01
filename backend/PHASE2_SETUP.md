# 🚀 CROP ZEN - PHASE 2 SETUP GUIDE

This guide walks you through setting up Crop Zen Phase 2 with database integration, authentication, and data persistence.

## Prerequisites

- Python 3.8+ installed
- pip package manager
- PostgreSQL 12+ installed and running
- Git (for version control)

## Step-by-Step Setup

### 1. Database Setup

#### Install PostgreSQL (if not already installed)
- **Windows**: Download from https://www.postgresql.org/download/windows/
- **Mac**: `brew install postgresql`
- **Linux**: `sudo apt-get install postgresql`

#### Create Database
```bash
# Start PostgreSQL service (varies by OS)
# Windows: PostgreSQL should auto-start, or use pgAdmin
# Mac/Linux: brew services start postgresql / sudo systemctl start postgresql

# Create crop_zen database
createdb -U postgres crop_zen

# Verify database was created
psql -U postgres -d crop_zen -c "SELECT 1;"
```

### 2. Python Dependencies

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installations
python -c "import sqlalchemy; import psycopg2; import jwt; import bcrypt; print('✅ All dependencies installed')"
```

### 3. Environment Configuration

The `.env` file has already been created with default values:
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/crop_zen
SECRET_KEY=dev-secret-key-please-change-in-production-32chars-min
FLASK_ENV=development
FLASK_DEBUG=True
FRONTEND_URL=http://localhost:3000
```

**For Production:**
- Change `SECRET_KEY` to a strong random value: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- Set `FLASK_ENV=production`
- Update `DATABASE_URL` with production credentials

### 4. Database Migration Setup

```bash
# Run Alembic setup automation
python setup_alembic.py

# This script will:
# 1. Initialize Alembic (if not already done)
# 2. Test database connection
# 3. Update Alembic configuration with DATABASE_URL
# 4. Create initial migration
# 5. Run migrations to create all tables

# If you want to do this manually:
# alembic init alembic
# alembic revision --autogenerate -m "Initial schema"
# alembic upgrade head
```

### 5. Verify Setup

```bash
# Test database connection
python -c "from database import test_connection; test_connection()"

# Test authentication utilities
python -c "from auth import test_password_hashing, test_jwt_tokens; test_password_hashing(); test_jwt_tokens()"
```

### 6. Start the Flask Application

```bash
# Development mode (with auto-reload and debug)
python app.py

# Or use Flask CLI
export FLASK_APP=app.py  # On Windows: set FLASK_APP=app.py
flask run

# Or use Gunicorn for production-like testing
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

The app should start on `http://localhost:5000`

## API Endpoints

### Authentication Endpoints
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/refresh-token` - Refresh access token
- `GET /api/auth/me` - Get current user info (requires token)

### Farm Management
- `GET /api/farms` - List user's farms (requires auth)
- `POST /api/farms` - Create new farm (requires auth)
- `GET /api/farms/<id>` - Get farm details (requires auth)
- `PUT /api/farms/<id>` - Update farm (requires auth)
- `DELETE /api/farms/<id>` - Delete farm (requires auth)

### Prediction Storage
- `GET /api/predictions` - List user's predictions (requires auth)
- `POST /api/predictions` - Store prediction (requires auth)

### Legacy Endpoints (without authentication for now)
- `POST /api/predict` - Crop prediction
- `GET /api/crops` - List supported crops
- `GET /health` - Health check

## Testing with curl

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

Response:
```json
{
  "status": "success",
  "message": "User registered successfully",
  "data": {
    "access_token": "eyJhbGc...",
    "refresh_token": "eyJhbGc...",
    "token_type": "Bearer",
    "user": {
      "id": 1,
      "email": "farmer@example.com",
      "first_name": "John",
      "last_name": "Farmer",
      ...
    }
  }
}
```

### Login User
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "farmer@example.com",
    "password": "SecurePass123"
  }'
```

### Get Current User (requires token)
```bash
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Create Farm
```bash
curl -X POST http://localhost:5000/api/farms \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
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

### Store Prediction
```bash
curl -X POST http://localhost:5000/api/predictions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
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

## Troubleshooting

### "psycopg2.OperationalError: could not connect to server"
- Make sure PostgreSQL is running
- Check DATABASE_URL in .env
- Verify database exists: `psql -U postgres -l`

### "ModuleNotFoundError: No module named 'sqlalchemy'"
- Run: `pip install -r requirements.txt`
- Activate virtual environment

### "ImportError: cannot import name 'init_db' from 'database'"
- Make sure you're in the correct directory
- Check that database.py exists in backend/

### Alembic migration issues
- Delete `alembic/` folder if corrupted: `rm -rf alembic/`
- Re-run: `python setup_alembic.py`

## Database Schema

### Users Table
- Stores user accounts with hashed passwords
- Fields: id, email, password_hash, first_name, last_name, phone, role, is_active

### Farms Table
- Stores multiple farms per user
- Fields: id, owner_id (FK), name, location, state, district, size_hectares, soil_type, latitude, longitude

### Predictions Table
- Stores crop predictions and model results
- Fields: id, farm_id (FK), crop_name, soil_ph, moisture, temperature, rainfall, confidence_score, season

### Other Tables
- SoilData: Stores soil analysis results
- DiseaseDetection: Stores disease detection model results
- Alert: Stores alerts for farmers

## Next Steps

1. **Start Frontend**: Set up React frontend (separate repository)
2. **Train ML Models**: Implement real crop recommendation and disease detection models
3. **Add Analytics**: Implement user dashboard and analytics
4. **Deploy**: Set up CI/CD and deploy to cloud (AWS, GCP, Azure, etc.)

## Production Checklist

- [ ] Change SECRET_KEY to strong random value
- [ ] Update DATABASE_URL with production credentials
- [ ] Set FLASK_ENV=production
- [ ] Use Gunicorn or similar WSGI server
- [ ] Enable HTTPS
- [ ] Set up proper logging and monitoring
- [ ] Configure firewall and security groups
- [ ] Set up automated backups
- [ ] Enable rate limiting and DDoS protection
- [ ] Set up CI/CD pipeline

## Support

For issues or questions:
1. Check logs: `logs/crop_zen.log`
2. Review error messages in terminal output
3. Consult API documentation: `backend/API_DOCUMENTATION.md`
4. Check this setup guide

---

**Last Updated:** 2024
**Phase 2 Status:** ✅ Ready for Testing & Integration
