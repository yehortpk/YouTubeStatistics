command = '/home/django/project1/env/bin/gunicorn'
pythonpath = '/home/django/code/project1/YouTubeStatistics'
bind = '127.0.0.1:8002'
workers = 1
user = 'django'
raw_env = 'DJANGO_SETTINGS_MODULE=YouTubeApi.settings'
