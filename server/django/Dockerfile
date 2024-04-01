FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV DB_DIR=/usr/src/inv-data

COPY . .

CMD [ "python", "./manage.py", "runserver", "0.0.0.0:8000" ]

