# Modular Structure Documentation

This Flask application has been refactored into a modular structure for better organization and maintainability.

## Directory Structure

```
audience-dropper/
├── app.py                 # Main application entry point
├── config.py             # Configuration settings
├── models/               # Database models and user classes
│   ├── __init__.py
│   └── user.py          # User model and database operations
├── routes/               # Route handlers organized by functionality
│   ├── __init__.py
│   ├── auth.py          # Authentication routes (signin, logout, request-access)
│   ├── main.py          # Main pages (index, dashboard, profile, account)
│   └── audiences.py     # Audience management routes
├── utils/                # Helper functions and utilities
│   ├── __init__.py
│   ├── audience_helpers.py  # Audience creation and management utilities
│   └── database.py      # Database initialization and connection utilities
└── templates/            # HTML templates (unchanged)
```

## Module Descriptions

### `app.py`
- Main application factory function
- Flask-Login setup
- Blueprint registration
- Application entry point

### `config.py`
- Centralized configuration settings
- Environment variable management
- Database connection settings

### `models/user.py`
- User class definition
- User database operations
- Flask-Login user loader function

### `routes/auth.py`
- Authentication-related routes
- Sign in/out functionality
- Access request handling

### `routes/main.py`
- Main application pages
- Dashboard, profile, and account pages
- Landing page

### `routes/audiences.py`
- Audience management routes
- 4-step audience creation workflow
- CSV download functionality

### `utils/audience_helpers.py`
- Audience creation helper functions
- LLM simulation functions
- CSV generation utilities
- Social platform search simulation

### `utils/database.py`
- Database connection management
- Database initialization utilities
- Collection and index setup

## Benefits of Modular Structure

1. **Separation of Concerns**: Each module has a specific responsibility
2. **Maintainability**: Easier to locate and modify specific functionality
3. **Scalability**: Easy to add new features by creating new modules
4. **Testability**: Individual modules can be tested in isolation
5. **Code Reusability**: Utility functions can be reused across different routes

## Usage

The application works exactly the same as before, but the code is now better organized. To run the application:

```bash
python app.py
```

## Adding New Features

To add new functionality:

1. **New Routes**: Create a new file in `routes/` directory
2. **New Models**: Add to `models/` directory
3. **New Utilities**: Add to `utils/` directory
4. **Register Blueprints**: Add new blueprints to `app.py`

## Database Operations

All database operations are now centralized in the appropriate modules:
- User operations: `models/user.py`
- Audience operations: `utils/audience_helpers.py`
- Database setup: `utils/database.py`
