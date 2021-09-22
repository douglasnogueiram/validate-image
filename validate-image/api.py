import flask
from flask import request, jsonify
from flask import Response

import os
import tensorflow as tf
import json
import jsonschema
from jsonschema import validate

import base64


checkImageSchema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "image": {"type": "string"}
    },
}

#define the image properties
image_width = 160
image_height = 160
image_color_channel = 3
image_color_channel_size = 255
image_size = (image_width, image_height)
image_shape = image_size + (image_color_channel,)


#validate if Json from request is valid
def validateJson(jsonData):
    try:
        validate(instance=jsonData, schema=checkImageSchema)
    except jsonschema.exceptions.ValidationError as err:
        return False
    return True


#load the model preprocessed
model = tf.keras.models.load_model('model')

#from a image, it returns a pet classification, between cat and dog 
def predict(image_file):

    try:    
        image = tf.keras.preprocessing.image.load_img(image_file, target_size = image_size)
        image = tf.keras.preprocessing.image.img_to_array(image)
        image = tf.expand_dims(image, 0)

        prediction = model.predict(image)[0][0]
        print('Prediction: {0} | {1}'.format(prediction, ('cat' if prediction < 0.5 else 'dog')))

    except:
        result = jsonify(
        image=image_file,
        prediction=0.0,
        pet='',
        result='error',
        message='Error to define the kind of pet'
        )

        
    else:
        result = jsonify(
        image=image_file,
        prediction=json.dumps(float(prediction)),
        pet=('cat' if prediction < 0.5 else 'dog'),
        result='success',
        message='detection ok'
        )
    return result  

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def hello_world():
    return 'Hello world'


@app.route('/api/v1/images', methods=['POST'])
def api_all():
    input_json = request.get_json(force=True)

    #validate json from request
    isValid = validateJson(input_json)
    if isValid:
        print("Given JSON data is valid")
        #print(input_json)
        if (input_json['image'] == 'margot5.jpg'):
            #prediction = predict('margot.jpg')
            prediction = predict(input_json['image'])
            print(prediction)
            return prediction
        else:
            imgstring = input_json['image']
            imgdata = base64.urlsafe_b64decode(imgstring)
            filename = input_json['name']
            with open(filename, 'wb') as f:
                f.write(imgdata)
            
            prediction = predict(filename)
            #print(prediction)
            return prediction
    else:
        print("Given JSON data is not valid")
        return Response(
        "Erro na chamada! Um ou mais campos informados estão incorretos...",
        status=400,
    )

app.run(host='0.0.0.0')