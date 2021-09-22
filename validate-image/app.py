import flask
from flask import request, jsonify

from time import sleep

import json
from json import loads
from json import dumps
from kafka import KafkaConsumer

from elasticsearch import Elasticsearch

import os

import jsonschema
from jsonschema import validate

import socket
import uuid

import tensorflow as tf

import base64

es = Elasticsearch()

#load the model preprocessed
model = tf.keras.models.load_model('model')

TOPIC_NAME = "images"
KAFKA_SERVER = "localhost:9092"

checkImageSchema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "image": {"type": "string"}
    },
}

consumer = KafkaConsumer(
    TOPIC_NAME,
     bootstrap_servers=['localhost:9092'],
     auto_offset_reset='earliest',
     enable_auto_commit=True,
     group_id='image-group',
     value_deserializer=lambda x: loads(x.decode('utf-8')))


#validate if Json from request is valid
def validateJson(jsonData):
    try:
        validate(instance=jsonData, schema=checkImageSchema)
    except jsonschema.exceptions.ValidationError as err:
        return False
    return True

#define the image properties
image_width = 160
image_height = 160
image_color_channel = 3
image_color_channel_size = 255
image_size = (image_width, image_height)
image_shape = image_size + (image_color_channel,)


#from a image, it returns a pet classification, between cat and dog 
def predict(image_file, jsonMessage):

    try:    
        image = tf.keras.preprocessing.image.load_img(image_file, target_size = image_size)
        image = tf.keras.preprocessing.image.img_to_array(image)
        image = tf.expand_dims(image, 0)

        prediction = model.predict(image)[0][0]
        print('Prediction: {0} | {1}'.format(prediction, ('cat' if prediction < 0.5 else 'dog')))

    except:
        result = json.dumps(
            {
            'image': image_file,
            'prediction' : 0.0,
            'pet' : '',
            'result' : 'error',
            'message' : 'Error to define the kind of pet',
            'timestamp' : jsonMessage['timestamp']
            }
        )

        
    else:
        result = json.dumps(
            {
            'image' : image_file,
            'prediction' : json.dumps(float(prediction)),
            'pet' : ('cat' if prediction < 0.5 else 'dog'),
            'result' : 'success',
            'message' : 'detection ok',
            'timestamp' : jsonMessage['timestamp']
            }
        )

    return result  



for message in consumer:
    message = message.value

    #validate json from request
    isValid = validateJson(message)
    if isValid:
        print("Given JSON data is valid")
        #print(input_json)
        if (message['image'] == 'margot5.jpg'):
            prediction = predict('margot5.jpg', message)
            print(prediction)
        else:
            try:
                imgstring = message['image']
                imgdata = base64.urlsafe_b64decode(imgstring)
                filename = message['name']
                with open(filename, 'wb') as f:
                    f.write(imgdata)
            
            except:
                print('Erro ao validar imagem')
            
            else:
                print('Sucesso ao validar mensagem')
                prediction = predict(filename, message)
                print(prediction)
                
                #Send to Elasticsearch
                res = es.index(index="test-index", id=message['id'], body=prediction)
                print(res['result'])
                
                os.remove(message['name'])
    else:
        print("Given JSON data is not valid")
        print("Erro na chamada! Um ou mais campos informados estão incorretos...")


