# Mosqku - Mosque Management System

A modern web application for managing multiple mosques. Streamline mosque administration with prayer time management, announcements and role-based access control.

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

### Vercel Deployment

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy:
```bash
vercel
```

4. For production deployment:
```bash
vercel --prod
```

### ⚠️ Important Notes
- For security reasons, please change the default superadmin password after your first login
- When deploying to Vercel, make sure to set up your environment variables in the Vercel dashboard
- The SQLite database will be recreated on each deployment, consider using a persistent database service for production

## 👥 User Roles & Capabilities

### Superadmin
- Manage all mosques in the system
- Create and edit mosque administrators
- Full system configuration access
- Assign administrators to any mosque
- Access to system-wide analytics

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
mosque-management-system/
├── api/
│   └── index.py         # Vercel entry point
├── main/
│   ├── __init__.py      # Application factory
│   ├── models/          # Database models
│   ├── controllers/     # Route handlers
│   ├── templates/       # HTML templates
│   └── static/          # Assets (CSS, JS)
├── instance/            # Database instance
├── requirements.txt     # Dependencies
├── vercel.json         # Vercel configuration
└── app.py              # Local development entry
```

## 🔒 Security Features

- SHA-256 password hashing
- Role-based access control
- Form validation with CSRF protection
- Secure session management
- Recovery key system for password reset
- Secure password requirements enforcement
- Rate limiting on sensitive endpoints
- XSS protection

## 📄 License

See [LICENSE](LICENSE) for details.