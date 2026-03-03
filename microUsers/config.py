import os


class Config:
    MYSQL_HOST = os.environ.get('DB_HOST', 'localhost')
    MYSQL_USER = os.environ.get('DB_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('DB_PASSWORD', 'root')
    MYSQL_DB = os.environ.get('DB_NAME', 'usersDB')
    SQLALCHEMY_DATABASE_URI = f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"

