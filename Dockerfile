FROM python:3.7
WORKDIR app

RUN pip install -U pip && pip install pipenv

COPY Pipfile* ./
RUN pipenv install --system

COPY . .

RUN python manage.py collectstatic

ENV DJANGO_SETTINGS_MODULE eclair.settings
ENV DJANGO_DEBUG True
CMD python manage.py runserver 0.0.0.0:8000
