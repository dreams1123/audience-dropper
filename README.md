# Audience Dropper

A modern web application for creating, managing, and optimizing target audiences for marketing campaigns. Built with Python Flask, MongoDB, and a clean white/light design using Tailwind CSS and Material UI.

## 🚀 Features

- **User Authentication**: Secure sign-in and access request system
- **Audience Management**: Create, edit, and manage target audiences
- **Advanced Targeting**: Demographics, interests, and custom criteria
- **Clean UI**: Modern white/light design with excellent UX
- **Responsive Design**: Works perfectly on desktop and mobile
- **Real-time Analytics**: Performance tracking and insights

## 🛠️ Tech Stack

- **Backend**: Python Flask
- **Database**: MongoDB
- **Frontend**: HTML, Tailwind CSS, Material UI Icons
- **JavaScript**: jQuery
- **Authentication**: Flask-Login
- **Forms**: WTForms with validation

## 📋 Prerequisites

- Python 3.8 or higher
- MongoDB (local or cloud)
- pip (Python package manager)

## 🚀 Installation

### Option 1: Automated Setup (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd audience-dropper

# Run the automated setup script
python setup.py
```

### Option 2: Manual Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd audience-dropper
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp env.example .env
   
   # The .env file is already configured with your MongoDB Atlas connection
   # You can modify the SECRET_KEY if needed
   ```

5. **Initialize the database**
   ```bash
   python init_db.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the application**
   - Open your browser and go to `http://localhost:5000`
   - Sign in with the test account: `admin@audiencedropper.com` / `admin123`
   - Or request access to create a new account
   - Start building your audiences!

## 🔐 Login Credentials

After running the database initialization, you can use these credentials:

**Test User:**
- Email: `admin@audiencedropper.com`
- Password: `admin123`

## 📁 Project Structure

```
audience-dropper/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── env.example           # Environment variables template
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html         # Base template with navigation
│   ├── index.html        # Landing page
│   ├── signin.html       # Sign-in page
│   ├── request_access.html # Access request form
│   ├── dashboard.html    # User dashboard
│   ├── profile.html      # User profile management
│   ├── account.html      # Account settings
│   ├── audiences.html    # Audiences overview
│   ├── create_audience.html # Create audience form
│   └── manage_audiences.html # Manage audiences table
└── .git/                 # Git repository
```

## 🎨 Design Philosophy

The application features a clean, modern white/light design that stands out with:

- **Minimalist Approach**: Clean lines and plenty of white space
- **Subtle Shadows**: Soft shadows for depth without being heavy
- **Blue Accent Color**: Professional blue (#3B82F6) for primary actions
- **Material Icons**: Consistent iconography throughout
- **Responsive Grid**: Flexible layouts that work on all devices
- **Hover Effects**: Subtle interactions for better UX

## 🔐 Security Features

- Password hashing with bcrypt
- Session management with Flask-Login
- CSRF protection
- Secure headers
- Input validation and sanitization

## 📊 Database Schema

### Users Collection
```javascript
{
  _id: ObjectId,
  email: String,
  password: String (hashed),
  name: String,
  role: String,
  company: String,
  created_at: Date,
  last_login: Date
}
```

### Audiences Collection
```javascript
{
  _id: ObjectId,
  user_id: String,
  name: String,
  description: String,
  category: String,
  criteria: String,
  status: String,
  created_at: Date,
  updated_at: Date
}
```

### Access Requests Collection
```javascript
{
  _id: ObjectId,
  name: String,
  email: String,
  company: String,
  reason: String,
  status: String,
  created_at: Date
}
```

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
1. Set `FLASK_ENV=production` in your environment
2. Use a production WSGI server like Gunicorn
3. Set up a reverse proxy (nginx)
4. Configure MongoDB for production
5. Set secure environment variables

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information

## 🔮 Future Enhancements

- [ ] Email notifications
- [ ] Advanced analytics dashboard
- [ ] API endpoints for external integrations
- [ ] Team collaboration features
- [ ] Advanced audience segmentation
- [ ] Campaign management
- [ ] A/B testing capabilities
- [ ] Export/import functionality

---

**Audience Dropper** - Transform your audience targeting strategy with precision and ease.
