### ecommerce-site-sports
An elegant ecommerce platform for selling sports items — built with Django, styled with Bootstrap 5, css and html, and powered by M-PESA Daraja API for seamless mobile payments.

![Build Status](https://img.shields.io/github/actions/workflow/status/pekimnjenga/ecommerce-site-sports/ci.yml?branch=main) ![Python Version](https://img.shields.io/badge/python-3.9%2B-blue) ![License](https://img.shields.io/github/license/pekimnjenga/ecommerce-site-sports)
![Pre-commit Enabled](https://img.shields.io/badge/pre--commit-enabled-brightgreen) ![Dockerized](https://img.shields.io/badge/docker-ready-blue) ![Render](https://img.shields.io/badge/deployed%20to-Render-blue) 
![Database](https://img.shields.io/badge/database-Supabase%20PostgreSQL-lightgrey) ![Framework](https://img.shields.io/badge/framework-Django-green) ![UI Framework](https://img.shields.io/badge/UI-Bootstrap%205-purple) ![Payment](https://img.shields.io/badge/payment-MPESA%20Daraja%20API-yellow)

### Table of Contents
- [ecommerce-site-sports](#ecommerce-site-sports)
- [Features](#features)
- [Tech Stack](#tech-stack)
  - [Backend](#backend)
  - [Frontend](#frontend)
  - [Payment Gateway](#payment-gateway)
  - [Deployment](#deployment)
  - [Cloud and Storage](#cloud-and-storage)
  - [CI/CD Automation](#cicd-automation)
  - [Version Control](#version-control)
- [Getting Started](#getting-started)
  - [Local Setup Instructions](#local-setup-instructions)
  - [Docker Setup](#docker-setup)
- [M-PESA Integration](#m-pesa-integration)
  - [STK Push Flow](#stk-push-flow)
  - [Setting Up M-PESA Daraja API](#setting-up-m-pesa-daraja-api)
    - [Sandbox (for development)](#sandbox-for-development)
    - [Production](#production)
- [Pre-commit Hooks](#pre-commit-hooks)
- [Deployment](#deployment)
- [Future Improvements](#future-improvements)
- [Contributing](#contributing)
- [License](#license)
- [Developer Contact](#developer-contact)
- [Acknowledgments](#acknowledgments)

### Project Description
**ecommerce-site-sports** is a modern e-commerce platform designed for selling sports items. It provides a seamless shopping experience with features like secure user authentication, a responsive product catalog, and integration with M-PESA Daraja API for mobile payments. The platform is ideal for businesses looking to offer sports merchandise online.

### Features
- User Authentication: Secure user registration and login with Django authentication.
- Product Catalog: Browse sports items organized by categories.
- Shopping Cart: Add, update, and remove items from the cart with real-time calculations.
- Multiple Product Images: Upload and display multiple images per item with carousel  slider.
- Size Selection: Choose item sizes (S, M, L, XL, etc.) during checkout.
- M-PESA Payment Integration: Seamless mobile payment processing via M-PESA Daraja API.
- Order Management: Track order status and delivery details.
- Admin Dashboard: Manage products, categories, orders, and user data.
- Responsive Design: Fully responsive for mobile, tablet, and desktop devices.
- Supabase Integration: Cloud storage for product images.
- Shipping & Return Policies: Clear, toggleable information for customers.
**NOTE**: The sports items for each category are few just to display and exhibit the website's logic

### Tech Stack

#### Backend
- **Framework**: Django — robust Python framework powering routing, logic, and server-side rendering
- **Database**: Supabase (PostgreSQL) — stores user data, transactions, and application content
- **Image Processing**: Pillow

#### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Custom styling and animations
- **Bootstrap 5**: Responsive layout and UI components

#### Payment Gateway
- **M-PESA Daraja API**: Handles secure STK Push requests and real-time payment callbacks

#### Deployment
- **Render**: Cloud-native hosting environment for the live application
- **Supabase**: Persistent cloud storage for database and media files

#### Cloud and Storage
- **Supabase**: Cloud database and image storage

#### CI/CD Automation
- **CI Automation**: GitHub Actions for automated code quality checks. On every push or pull request to `main`, the following checks run automatically via `.github/workflows/ci.yml`:
  - `black` — ensures consistent code formatting
  - `isort` — enforces import order
  - `flake8` — flags style and syntax issues
- **CD Automation**: The project gets automatically deployed to Render after passing all testing and quality checks.

#### Version Control
- **GitHub**: Source code management and collaboration



### Getting Started
#### (a) Local Setup Instructions
1. Clone the Repository
```bash
git clone https://github.com/your-username/ecommerce-site-sports.git
cd ecommerce-site-sports
```
2. Create and Activate Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install Dependencies
```bash
pip install -r requirements.txt
```
4. Configure Environment Variables
Create a .env file and add:

```env
# For any other database apart from sqlite i.e postgres, mysql
DATABASE_NAME=your_db_name
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password
DATABASE_HOST=your_db_host
DATABASE_PORT=your_db_port

MPESA_CONSUMER_KEY=your_sandbox_key
MPESA_CONSUMER_SECRET=your_sandbox_secret
MPESA_SHORTCODE=your_shortcode
MPESA_PASSKEY=your_passkey
MPESA_CALLBACK_URL=https://yourdomain.com/callback/
```
If you're using PostgreSQL or MySQL instead of SQLite, update your DATABASES setting in settings.py like this:
```settings
DATABASES = {
    'default': {
        # For PostgreSQL
        'ENGINE': 'django.db.backends.postgresql',
        
        # For MySQL
        # 'ENGINE': 'django.db.backends.mysql',

        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST'),
        'PORT': os.getenv('DATABASE_PORT'),
    }
}
```
then load the environment variables at the top of the script using dotenv 
```settings
from dotenv import load_dotenv
load_dotenv()
```

5. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```
6. Create a Superuser(Admin Account)
```bash
python manage.py createsuperuser
```
7. Collect Static Files
```bash
python manage.py collectstatic --noinput
```
8. Start the Server
```bash
python manage.py runserver
```
Visit https://127.0.0.1:8000 in your browser


#### (b) Docker Setup
1. Build the Image
```bash
docker build -t ecommerce-site-sports .
```
2. Run the Container
```bash
docker run --env-file .env -p 8000:8000 ecommerce-site-sports
```


### M-PESA Integration
#### STK Push Flow
1. User adds items to cart
2. Enters phone number and address
3. Receives STK Push prompt
4. Upon confirmation, redirected to success page

#### Setting Up M-PESA Daraja API
##### Sandbox (for development)
- Go to the official M-PESA Developer Portal: https://developer.safaricom.co.ke
- Create an account and log in
- Navigate to My Apps and create a new application
- Choose an API product to map to your app(select all)
- After creating the app, you'll receive:
  Consumer Key
  Consumer Secret
- To obtain the Shortcode and Passkey;
  Go to APIs
  Click Simulate under the M-PESA Express section
  Choose your app in the simulator dropdown
  You’ll see your credentials including:
    Shortcode: 174379 (default sandbox shortcode)
    Passkey: bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919 (static sandbox passkey)

- Add to .env file
```bash
MPESA_CONSUMER_KEY=your_sandbox_key
MPESA_CONSUMER_SECRET=your_sandbox_secret
MPESA_SHORTCODE=174379
MPESA_PASSKEY=bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919
MPESA_CALLBACK_URL=https://yourdomain.com/callback/
```
For MPESA_CALLBACK_URL, use your exposed ngrok URL during local development, and also make sure the exposed ngrok url is trusted by csrf
```settings
CSRF_TRUSTED_ORIGINS = [
    "yourngrokurl",
]
```


##### Production
- Apply for an M-PESA shortcode, username, and organization name.
- Request Safaricom to send administrator logins via m-pesabusiness@safaricom.co.ke.
- After entering the shortcode, username, and organization name, select API products and  enter the OTP sent to your email.
- Safaricom will email you a passkey. Your live app credentials will include:
  Consumer Key
  Consumer Secret
  Shortcode

### Pre-commit Hooks
This project uses [pre-commit](https://pre-commit.com/) to enforce code quality and security checks before each commit.
1. Install Pre-commit
```bash
pip install pre-commit
```
2. Install the Git Hooks
```bash
pre-commit install
```
3. Configure .pre-commit-config.yml
```bash
repos:
  - repo: https://github.com/psf/black
    rev: 25.9.0
    hooks:
      - id: black
        args: [--check]

  - repo: https://github.com/PyCQA/flake8
    rev: 7.3.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-isort
    rev: v5.10.1
    hooks:
      - id: isort
        args: [--check-only]
```
4. Run the pre-commit hook
```bash
pre-commit run --all-files
```


### Deployment
1. Create a Render Account: Visit Render.com
2. Connect Your GitHub Repository:
   New Web Service → Connect GitHub
   Select your repository
3. Configure Build Settings:
   Build Command: pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
   Start Command: gunicorn store.wsgi:application
4. Set Environment Variables
   Add all variables from your .env file to Render's 'Environment' section in the dashboard
5. Deploy:
   Render will automatically deploy on every push to main

### Future Improvements
 - **Advanced Search & Filtering**: Implement search with autocomplete and multiple filters (price range, size, color, rating).
 - **Product Reviews & Ratings**: Allow customers to rate and review products.
 - **Wishlist Feature**: Let users save favorite items for later.
 - **Order Tracking**: Real-time tracking with SMS/email notifications.


### Contributing
Contributions are welcome. To contribute:
1. Fork the Repository
2. Clone Your Fork Locally
```bash
git clone https://github.com/yourusername/realestate.git
cd realestate
```
3. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```
4. Make Your Changes
   Write clean, well-documented code
   Follow PEP 8 style guide
   Run pre-commit hooks before committing

5. Commit your changes
```bash
git commit -m "Add: Brief description of your changes"
```
6. Push to your fork
```bash
git push origin feature/your-feature-name
```
7. Open a Pull Request
- Go to your fork on GitHub
- Click "Compare & pull request"
- Fill in the title and description
  Describe what your changes do
  Reference any related issues (e.g., )
- Submit and wait for review


### License
This project is open-source under the MIT License - see the LICENSE file for details.

### Developer Contact
Developed and maintained by PEKIM
 Email: njengapekim@gmail.com 
 Phone: +254 797933409
 GitHub: [github.com/pekimnjenga](https://github.com/pekimnjenga)

### Acknowledgements
- [Django Documentation](https://docs.djangoproject.com/)
- [Bootstrap 5](https://getbootstrap.com/)
- [Mpesa Daraja API](https://developer.safaricom.co.ke/)
- [Supabase](https://supabase.com/)
- [Render](https://render.com/)
- [pre-commit](https://pre-commit.com/)
- [Github](https://github.com)