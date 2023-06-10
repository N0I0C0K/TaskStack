FROM python:3.11-alpine3.18

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt

# port for the server is 5555
CMD [ "python3", "Server.py" ]