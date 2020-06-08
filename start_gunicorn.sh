#!/bin/bash
source /home/django/code/project1/env/bin/activate
exec gunicorn -c "/home/django/code/project1/YouTubeStatistics/gunicorn_config.py" YouTubeApi.wsgi
