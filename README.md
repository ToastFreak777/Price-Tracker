# Price-Tracker

A Flask-based web application that tracks product prices across multiple vendors, maintains price history, and allows users to set target price alerts.

## 📋 Features

- **User Authentication**: Secure registration and login system with password hashing
- **Price Tracking**: Monitor product prices from multiple vendors (Mock and eBay datasources)
- **Price History**: Track and visualize price changes over time
- **Target Price Alerts**: Set custom price targets for tracked items
- **Notification Management**: Enable/disable notifications per user or per item
- **Demo Mode**: Try the application without creating an account
- **RESTful API**: JSON API endpoints for programmatic access

## 🛠 Tech Stack

- **Backend**: Flask 3.x
- **Database**: SQLAlchemy 2.x with SQLite (configurable)
- **Migrations**: Flask-Migrate/Alembic
- **Authentication**: Flask-Login with secure password hashing
- **Forms**: Flask-WTF with CSRF protection
- **Testing**: pytest with coverage
- **Validation**: email-validator, WTForms validators
- **HTTP Requests**: requests library for API calls

## 📁 Project Structure

```
Price-Tracker/
├── ptracker/                       # Main application package
│   ├── __init__.py                 # App factory and initialization
│   ├── models.py                   # Database models (User, Item, UserItem, PriceHistory)
│   ├── extensions.py               # Flask extensions (db, login_manager)
│   ├── dependencies.py             # Dependency injection setup
│   ├── errors.py                   # Error handlers
│   ├── commands.py                 # CLI commands
│   ├── notifications.py            # Notification system
│   ├── auth/                       # Authentication blueprint
│   │   ├── routes.py               # Auth routes (login, register, logout)
│   │   ├── service.py              # Auth business logic
│   │   └── forms.py                # Auth forms
│   ├── price_tracking/             # Price tracking blueprint
│   │   ├── routes.py               # Item tracking routes
│   │   ├── service.py              # Price tracking business logic
│   │   └── forms.py                # Item tracking forms
│   ├── main/                       # Main blueprint
│   │   └── routes.py               # Home page
│   ├── api/                        # API blueprint
│   │   └── routes.py               # JSON API endpoints
│   ├── datasources/                # Data source adapters
│   │   ├── base.py                 # Base datasource interface
│   │   ├── mock.py                 # Mock datasource for testing
│   │   └── ebay.py                 # eBay datasource
│   ├── static/                     # CSS, JS, images
│   └── templates/                  # Jinja2 templates
├── tests/                          # Test suite
│   ├── conftest.py                 # pytest fixtures
│   ├── integration/
│   │   ├── http/                   # HTTP endpoint tests
│   │   └── service/                # Service layer tests
├── migrations/                     # Database migrations
├── config.py                       # Configuration settings
├── run.py                          # Application entry point
├── seed.py                         # Database seeding script
├── requirements.txt                # Python dependencies
└── pytest.ini                      # pytest configuration
```

## 🚀 Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/ToastFreak777/Price-Tracker.git
   cd Price-Tracker
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file in the root directory:

   ```env
   FLASK_APP=ptracker
   FLASK_ENV=development
   FLASK_DEBUG=true
   SECRET_KEY=your-secret-key-here
   DB_URI=sqlite:///site.db
   EBAY_CLIENT_ID=your-ebay-client-id (optional)
   EBAY_CLIENT_SECRET=your-ebay-client-secret (optional)
   ```

5. **Initialize the database**

   ```bash
   flask db upgrade
   ```

6. **Run the application**

   ```bash
   python run.py
   ```

   Or

   ```bash
   flask run
   ```

   The application will be available at `http://localhost:5000`

## 🧪 Testing

Run the complete test suite:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=ptracker --cov-report=html
```

Run specific test files:

```bash
pytest tests/integration/service/test_auth_service.py
pytest tests/integration/http/test_auth_routes.py
```

## 📖 Usage

### Web Interface

1. **Register an account** at `/auth/register`
2. **Login** at `/auth/login`
3. **Add items to track** at `/items/add`
4. **View tracked items** on the home page `/home`
5. **View item details** and price history by clicking on an item
6. **Manage alerts** at `/items/alerts`
7. **Update user settings** at `/auth/user/settings`

### Demo Mode

Try the application without creating an account by clicking the "Demo" button on the login page.

### API Endpoints

#### Authentication

- `POST /api/register` - Register a new user
- `POST /api/login` - Log in an existing user
- `POST /api/logout` - Log out the current user
- `DELETE /api/user/<user_id>` - Delete user account

#### Price Tracking

- `GET /api/items/<item_id>` - Get item details and price history
- `DELETE /api/items/<item_id>` - Untrack an item
- `PATCH /api/user/notifications` - Update user notification settings
- `PATCH /api/items/<item_id>/notifications` - Update item notification settings
- `GET /api/update-items` - Trigger price update for all tracked items

Example API request:

```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

## 🗄 Database Models

### User

- Stores user credentials and preferences
- Relationships: tracked_items through UserItem

### Item

- Stores product information from vendors
- Fields: vendor, external_id, url, name, price, currency, stock status
- Relationships: price_history, user_items

### UserItem

- Junction table linking users to tracked items
- Fields: user_id, item_id, target_price, notifications_enabled

### PriceHistory

- Historical price records for items
- Fields: item_id, price, timestamp

## 🔌 Data Sources

### Mock Datasource

- Always enabled for testing
- URLs matching `mock.com` pattern
- Returns mock product data

### eBay Datasource

- Enabled when `EBAY_CLIENT_ID` is configured
- Fetches real product data from eBay API

## 🛡 Security Features

- Password hashing using Werkzeug's security helpers
- CSRF protection on all forms
- Flask-Login session management
- User role system (user, demo, admin)
- Protected API endpoints requiring authentication

## 📝 CLI Commands

The application includes custom Flask CLI commands:

```bash
flask seed-db      # Seed database with sample data
flask init-db      # Initialize database tables
```

## 🔮 Future Enhancements

- [ ] Add more vendor datasources (Amazon, Walmart, etc.)
- [ ] SMS notifications for price drops
- [ ] Export price history data (CSV, JSON)
- [ ] Search functionality for tracked items
