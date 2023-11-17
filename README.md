# YouTubeStatistics

[![Static Badge](https://img.shields.io/badge/Python-3.8-yellow.svg)](https://www.python.org/downloads/release/python-380/)
[![Static Badge](https://img.shields.io/badge/Django-3.2-green)](https://docs.djangoproject.com/en/3.2/)
[![Static Badge](https://img.shields.io/badge/MySQL-8-blue)]([https://developer.mozilla.org/en-US/docs/Web/CSS](https://dev.mysql.com/doc/relnotes/mysql/8.0/en/))
[![Static Badge](https://img.shields.io/badge/HTML-5-red)](https://developer.mozilla.org/en-US/docs/Glossary/HTML5)
[![Static Badge](https://img.shields.io/badge/CSS-3-blue)](https://developer.mozilla.org/en-US/docs/Web/CSS)
[![Static Badge](https://img.shields.io/badge/JS-yellow)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)

## Description
This is a project that shows all channel statistics, including your subscriptions.

After signing in with Google, all your subscription channels will be displayed. Each channel has its own statistics with a set of videos on it.
Each video has its own parameters like likes, views, comments, etc.

## Environment variables
To run this project, you will need to add the following environment variables to your db.env file:

`MYSQL_DATABASE` - database name

`DB_USER` - database user (for Django MySQL driver)

`DB_PASSWORD` - database password (for Django MySQL driver)

`MYSQL_ROOT_PASSWORD` - database root password

## Run Locally

Clone the project

```bash
  git clone https://github.com/yehortpk/YouTubeStatistics.git
```

Go to the project directory

```bash
  cd YouTubeStatistics
```

Run docker compose in debug mode (currently only debug available)

```bash
 docker-compose up --build
```

Create Google app info file (next step)

## Google App Info file (info.json)
To run this project, you will need to create the Google app info file. To do this, you have to go to https://console.cloud.google.com/, then:
- Open navigation menu
- Go to APIs & Services > Credentials
- CREATE CREDENTIALS > OAuth cliend ID
- Application type - Web application
- Add origins - `http://localhost:8000`
- Add redirect uri - `http://localhost:8000/token`
- Create
- Download json
- Put it in static directory

## License

MIT License

Copyright (c) 2023

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS," WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT, OR OTHERWISE, ARISING FROM, OUT OF, OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

