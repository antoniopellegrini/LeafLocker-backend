# Backend Tesi
## Setup
* git init
* git clone https://antoniopellegrini@bitbucket.org/tesi-leaf/be-monolithic.git -b develop
* python -m venv venv
* pip install -r requirements.txt

## Database migrations
* flask db init (first setup)
* flask db migrate -m "Migration message"
* flask db upgrade/downngrade