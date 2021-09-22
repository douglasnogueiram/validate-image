FROM python:3.8-slim-buster

# We copy just the requirements.txt first to leverage Docker cache

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app

RUN pip install kafka-python
RUN pip install future
RUN pip install tensorflow
RUN pip install -U matplotlib
RUN pip install jsonschema
RUN pip install flask cors

ENTRYPOINT [ "python" ]

CMD [ "app.py" ]