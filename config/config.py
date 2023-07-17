from datetime import timedelta
import os

SQLALCHEMY_DATABASE_URI = ''
RDS_USERNAME = os.environ.get('RDS_USERNAME')
RDS_PASSWORD = os.environ.get('RDS_PASSWORD')
RDS_HOSTNAME = os.environ.get('RDS_HOSTNAME')
RDS_PORT = os.environ.get('RDS_PORT')
RDS_DB_NAME = os.environ.get('RDS_DB_NAME')
SECRET_KEY = os.environ.get('SECRET_KEY')
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)  # seconds=43200 -> 12h
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)  # seconds=43200 -> 12h
SQLALCHEMY_TRACK_MODIFICATIONS = True
PROPAGATE_EXCEPTIONS = True
JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
TESTING = False

# ---- DATABASE CONFIGURATION ----

host = ''
is_aws = True if os.environ.get("IS_AWS") else False
if (is_aws):
    host = 'aws'
else:
    host = 'local'

if host == "aws":
    SQLALCHEMY_DATABASE_URI = f'mysql://{RDS_USERNAME}:{RDS_PASSWORD}@{RDS_HOSTNAME}:{RDS_PORT}/{RDS_DB_NAME}'

if host == "local":
    SQLALCHEMY_DATABASE_URI = f"mysql://root:{os.environ.get('DATABASE_PASSWORD')}@127.0.0.1:3308/db_tesi"

if host == "sqlite":
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data.db'
