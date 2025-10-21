# SecureBank - Advanced Online Banking Platform

A comprehensive, secure online banking application built with Django, featuring cryptocurrency trading, gift card transactions, and extensible service integration.

## 🚀 Features

### Core Banking
- ✅ Secure user authentication with email-based login
- ✅ Multi-factor authentication (2FA) support
- ✅ KYC (Know Your Customer) verification system
- ✅ Multiple account types (Savings, Current, Business, Crypto)
- ✅ Real-time transaction processing
- ✅ Beneficiary management
- ✅ Scheduled transactions

### Cryptocurrency
- ✅ Multi-crypto wallet support (BTC, ETH, USDT, etc.)
- ✅ Buy/Sell/Transfer cryptocurrencies
- ✅ Portfolio management and tracking
- ✅ Real-time price monitoring
- ✅ Crypto watchlist

### Gift Cards
- ✅ Gift card trading platform
- ✅ Support for major retailers
- ✅ Instant verification system
- ✅ Competitive rates
- ✅ Dispute resolution

### Payment Services
- ✅ Paystack integration for payments
- ✅ Airtime top-up
- ✅ Bill payments (Electricity, Water, Internet)
- ✅ School fee payments
- ✅ Extensible service architecture

### Security
- 🔒 Military-grade encryption
- 🔒 CSRF protection
- 🔒 Rate limiting
- 🔒 Input validation
- 🔒 Secure session management
- 🔒 Audit logging
- 🔒 Account lockout protection

## 🛠 Technology Stack

- **Backend**: Django 5.2.7, Django REST Framework
- **Frontend**: Bootstrap 5, jQuery, AJAX
- **Database**: SQLite (development), PostgreSQL (production)
- **Payment**: Paystack SDK
- **Security**: Django Two-Factor Auth, Cryptography
- **Deployment**: Render, Gunicorn, WhiteNoise

## 📋 Requirements

- Python 3.11+
- Node.js (for frontend assets, optional)
- PostgreSQL (for production)

## 🚀 Quick Start

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd securebank
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Start development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Frontend: http://localhost:8000
   - Admin: http://localhost:8000/admin

## 🏗 Project Structure

```
securebank/
├── accounts/          # User management and authentication
├── transactions/      # Financial transactions
├── payments/         # Payment processing (Paystack)
├── crypto/           # Cryptocurrency features
├── giftcards/        # Gift card trading
├── services/         # Additional services (airtime, bills)
├── templates/        # HTML templates
├── static/          # CSS, JavaScript, images
├── media/           # User uploads
└── securebank/      # Main project settings
```

## 🔧 Configuration

### Environment Variables

Key environment variables in `.env`:

```env
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,yourdomain.com

# Paystack
PAYSTACK_PUBLIC_KEY=your-paystack-public-key
PAYSTACK_SECRET_KEY=your-paystack-secret-key

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Security Settings

The application includes comprehensive security configurations:

- HTTPS enforcement
- Secure cookies
- XSS protection
- CSRF protection
- Content Security Policy
- Rate limiting

## 🚀 Deployment

### Render Deployment

1. **Connect repository to Render**
2. **Configure environment variables**
3. **Deploy automatically**

The application includes:
- `render.yaml` - Render configuration
- `Procfile` - Process configuration
- Production-ready settings

### Manual Deployment

1. **Set up production database**
2. **Configure environment variables**
3. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```
4. **Run with Gunicorn**
   ```bash
   gunicorn securebank.wsgi:application
   ```

## 📊 API Documentation

### Authentication Endpoints

- `POST /api/v1/auth/login/` - User login
- `POST /api/v1/auth/register/` - User registration
- `POST /api/v1/auth/logout/` - User logout
- `GET /api/v1/auth/profile/` - User profile

### Transaction Endpoints

- `GET /api/v1/transactions/` - List transactions
- `POST /api/v1/transactions/transfer/` - Initiate transfer
- `GET /api/v1/transactions/history/` - Transaction history

### Crypto Endpoints

- `GET /api/v1/crypto/wallets/` - List crypto wallets
- `POST /api/v1/crypto/buy/` - Buy cryptocurrency
- `POST /api/v1/crypto/sell/` - Sell cryptocurrency

## 🧪 Testing

Run tests with:
```bash
python manage.py test
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 Support

For support and inquiries:
- Email: iyanuolalegan1@gmail.com
- Documentation: [Wiki](#)
- Issues: [GitHub Issues](#)

## 🔐 Security

For security concerns, please email: iyanuolalegan1@gmail.com

---

**Built with ❤️ for secure digital banking**# Securebank
