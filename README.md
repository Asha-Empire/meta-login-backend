# meta-login-backend
Companion backend for the UE5 multiplayer template (5 core classes): secure login/registration, token auth, and scalable player services.

# Setup

`cd meta-login-backend`<br>
`python -m venv .venv`<br>
`.venv\\Scripts\\activate.ps1 or .venv\\Scripts\\activate.bat`<br>
`pip install -r requirements.txt`<br>
`python manage.py makemigrations` if needed<br>
`python manage.py migrate`<br>
`python manage.py runserver 0.0.0.0:9711`<br>
