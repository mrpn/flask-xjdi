---
title: Flask
description: A popular minimal server framework for Python
tags:
  - python
  - flask
---

# Python Flask Example

This is a [Flask](https://flask.palletsprojects.com/en/1.1.x/) app that serves a simple JSON response.

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/zUcpux)

## ✨ Features

- Python
- Flask

## 💁‍♀️ How to use

- Install Python requirements `pip install -r requirements.txt`
- Start the server for development `python3 main.py`

## Local development

`export FLASK_APP=run.py` to add to shell or `python run.py` for dev

to register commands python run.py register

```bash
virtualenv venv
source venv/bin/activate

gunicorn -b 0.0.0.0:$PORT -w 1 app:app
```
