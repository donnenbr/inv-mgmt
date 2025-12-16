FROM python:3.12
ENV KING_BEAR=bobby
ENV DB_TYPE=postgres
# RUN mkdir /app
WORKDIR /app
COPY --from=root requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt
COPY --from=root *.py .
CMD [ "gunicorn", "--config", "gunicorn_config.py", "invmgmt.main:app" ]



