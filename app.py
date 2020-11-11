import paho.mqtt.client as mqtt
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)

# The callback for whem the client recieves a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code"+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and 
    # reconnect then sunscriptions will be renewed
    client.subscribe("/esp32/pub")
   #  client.subscribe("/esp8266/humidity")
# The callback for when a PUBLISH message is recieved from the ESP8266.
def on_message(client, userdata, message):

    print("Received message '" + str(message.payload) +"'on topic'"
    +message.topic)
   #  if message.topic == "/esp8266/temperature":
   #      print("temperature update")
   #      socketio.emit('dht_temperature', {'data': message.payload})
   #  print("Received message '" + str(message.payload) +"'on topic'"
   #  +message.topic)
   #  if message.topic == "/esp8266/humidity":
   #      print("humidity update")
   #      socketio.emit('dht_humidity', {'data': message.payload})



mqttc=mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.connect("localhost",1883,60)
mqttc.loop_start()

# Create a dictionary called pins to store the pin number, name, and pin state:
pins = {
   4 : {'name' : 'LED1', 'board' : 'esp8266', 'topic' : '/esp8266/LED1', 'state' : 'False'},
   5 : {'name' : 'LED2', 'board' : 'esp8266', 'topic' : '/esp8266/LED2', 'state' : 'False'}
   }

# Put the pin dictionary into the template data dictionary:
templateData = {
   'pins' : pins
   }

@app.route("/")
def main():
   mqttc.publish("/esp32","Hola")
   # Pass the template data into the template main.html and return it to the user
   return render_template('main.html', **templateData)

# The function below is executed when someone requests a URL with the pin # number and action in it:
@app.route("/<board>/<changePin>/<action>")

def action(board, changePin, action):
   # Convert the pin from the URL into an integer:
   changePin = int(changePin)
   # Get the device name for the pin being changed:
   devicePin = pins[changePin]['name']
   # If the action part of the URL is "on," execute the code indented below:
   if action == "1" and board == 'esp8266':
      mqttc.publish(pins[changePin]['topic'],"1")
      pins[changePin]['state'] = 'True'

   if action == "0" and board == 'esp8266':
      mqttc.publish(pins[changePin]['topic'],"0")
      pins[changePin]['state'] = 'False'

   # Along with the pin dictionary, put the message into the template data dictionary:
   templateData = {
      'pins' : pins
   }

   return render_template('main.html', **templateData)

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=8181, debug=True)
