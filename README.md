### ecommerce-site-sports
An simple ecommerce platform for selling sports items — built with Django, styled with Bootstrap 5, css and html, and powered by M-PESA Daraja API for seamless mobile payments.

### Features
- Add sports items to cart
- Enter phone number and address
- Receive M-PESA STK Push prompt
- Redirected to a success page upon payment confirmation
- Contains orders page for tracking the order,i.e, order ID, items ordered and delivery status
- Payment audit and callback handling via Daraja API
- Deployed on [Render](https://render.com)
- Database hosted on [Supabase](https://supabase.com)

### Tech Stack
- Backend: Django — robust Python framework powering routing, logic, and server-side rendering
- Frontend: HTML, CSS, and Bootstrap 5 — responsive layout, UI components, and styling
- Payment Integration: M-PESA Daraja API — handles secure STK Push requests and real-time payment callbacks
- Database: Supabase (PostgreSQL) — stores user data, transactions, and application content
- Deployment: Render — cloud-native hosting environment for the live application
- CI/CD Automation
    CI Automation - This project uses GitHub Actions for automated code quality checks and test coverage enforcement.On every push  or pull request to main, the following checks run automatically via .github/workflows/ci.yml:
      black — ensures consistent code formatting
      isort — enforces import order
      flake8 — flags style and syntax issues
      safety — checks for insecure dependencies
    CD Automation - The project gets automatically deployed to Render after passing all testing and quality checks
- Version Control: GitHub — source code management and collaboration

### Running instructions
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
python manage.py migrate
```
6. Start the Server
```bash
python manage.py runserver
```
#### (b) Docker Setup
1. Build the Image
```bash
docker build -t ecommerce-site-sports .
```
2. Run the Container
```bash
docker run --env-file .env -p 8000:8000 ecommerce-site-sports
```


### M-PESA Sandbox Integration
This project uses Safaricom’s [Daraja API Sandbox](https://developer.safaricom.co.ke/daraja/apis/post/safaricom-sandbox) for development.

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
- You must have an mpesa shortcode, username and organisation name(if you don't have a shortcode apply for one, and also request Safaricom via m-pesabusiness@safaricom.co.ke to send you the administrator logins i.e username and password, since you'll need the username during the process of going live.I'll soon write a blog on how to apply for the shortcode and other credentials i.e username)
- After entering the mpesa shortcode, username and organisation name you will be redirected to a page where you will select the API products and enter an OTP which will be sent to your email.
- After the above process Safaricom will email you a passkey, then your live app will now be visible after you go to 'My Apps' and click on the dropdown at the 'Active entity' section. The app will have the credentials required i.e Consumer key, Consumer secret and the shortcode. 

### Pre-commit Hooks
This project uses [pre-commit](https://pre-commit.com/) to enforce code quality and security checks before each commit.
To set it up locally:

```bash
pip install pre-commit
pre-commit install
```
This activates hooks for:
  black — code formatting
  isort — import sorting
  flake8 — style and syntax checks
NOTE : There is no official pre-commit hook for safety maintained by Safety CLI or PyUp, but you can still run safety in CI or manually
```bash
safety check --full-report --file=requirements.txt
```

### Deployment Notes
- Render handles static/media files via Django’s collectstatic and /media/ folder
- Supabase PostgreSQL is used for persistent cloud storage
- Migrations and creation of the static folder are applied via Render shell:
```bash
python manage.py collectstatic --noinput #If you are using render's free plan, but if you have a paid instance add this as your post-build command
python manage.py migrate
```

### Developer Contact
Developed and maintained by PEKIM
 Email: njengapekim@gmail.com 
 Phone: +254 797933409
 GitHub: [github.com/pekimnjenga](https://github.com/pekimnjenga)


### Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you’d like to change.

### License
This project is open-source under the MIT License.

