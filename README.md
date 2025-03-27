# Mosqku - Mosque Management System

A modern web application for managing multiple mosques (#GodamSahur 2025)

## ✨ Key Features

- 🕌 **Multi-mosque Support**
  - Manage multiple mosques from one platform
  - Detailed mosque information management
  - Capacity and contact tracking
- 🕒 **Prayer Time Management**
  - Schedule and update prayer times
  - Daily prayer time display with proper ordering (Imsak, Subuh, Syuruk, Zuhur, Asar, Maghrib, Isyak)
  - Automatic scheduling
- 📢 **Announcement System**
  - Create and manage announcements
  - Set announcement duration
  - Target specific audiences
- 👥 **Role-based Access Control**
  - Superadmin: Full system access and mosque management
  - Admin: Mosque-specific management and ability to add co-administrators
  - User: View mosque information
- 🔐 **Account Security**
  - Recovery key system for password reset
  - Secure password requirements
  - View recovery key functionality
  - Password reset with recovery key
- 📦 **Inventory Management**
  - Track mosque assets and equipment
  - Manage maintenance schedules
  - Record item conditions and locations
- 💰 **Financial Management**
  - Track donations and expenses
  - Generate financial reports
  - Manage mosque budgets

## 🚀 Quick Start

### Local Development

1. Clone and enter the repository:
```bash
git clone https://github.com/ikmalsaid/mosqku.git
cd mosqku
```

2. Set up Python environment:
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Unix/MacOS
source venv/bin/activate
```

3. Install and initialize:
```bash
pip install -r requirements.txt
python app.py
```

4. Access the application:
- Open `http://localhost:5000`
- Login with default superadmin account:
  ```
  Email: admin@mosqku.com
  Password: Admin@123
  ```
- Or create a new account

### ⚠️ Important Notes
- For security reasons, please change the default superadmin password after your first login
- The SQLite database will be recreated on each deployment, consider using a persistent database service for production

## 👥 User Roles & Capabilities

### Superadmin
- Manage all mosques in the system
- Create and edit mosque administrators
- Full system configuration access
- Assign administrators to any mosque

### Admin
- Manage assigned mosque details
- Control prayer times and announcements
- Add co-administrators to their mosque
- Manage mosque inventory and finance
- View and manage mosque-specific administrators

### User
- View mosque information
- Access prayer times
- Read announcements
- View mosque inventory status
- Access public financial reports

## 🏗️ Project Structure
```
mosqku/
├── main/
│   ├── static/          # Assets (CSS, JS)
│   ├── models/          # Database models
│   ├── controllers/     # Route handlers
│   ├── templates/       # HTML templates
│   └── __init__.py      # Main server file
├── instance/            # Database instance
├── requirements.txt     # Dependencies
└── app.py               # Application file
```

## 🔒 Security Features

- Scrypt password hashing
- Role-based access control
- Form validation with CSRF protection
- Secure session management
- Recovery key system for password reset
- Secure password requirements enforcement

## 📄 License

See [LICENSE](LICENSE) for details.