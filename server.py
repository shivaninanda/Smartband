from flask import Flask, jsonify, request, send_from_directory
import flask
import requests
import time
import pickle
import os

goog_key = 'AIzaSyCDJOnX2k4ZMY0ziRpPW8glBhgycbH2gxw'
url = 'https://www.googleapis.com/geolocation/v1/geolocate'   

location_file_name = 'location.txt'

app = Flask(__name__)

@app.route('/', methods = ['GET'])
def root():
	return send_from_directory(os.getcwd(), 'index.html')

@app.route('/location', methods = ['GET'])
def get_location():
	if os.path.exists(location_file_name):
		location_file = open(location_file_name)
		location = pickle.load(location_file)
		location_file.close()
		print(location)
		return jsonify(location)
	else:	
		return jsonify({})

@app.route('/location', methods = ['PUT'])
def update_location():
	print('The Headers:\n"%s"' % str(request.headers))
	print('The Data:\n"%s"' % str(request.data))
	all_locations = str(request.data).split("\n")
	valid_locations = filter(lambda x: x.startswith("+CWLAP") and x.endswith(')'), all_locations)
	access_points = []
	if len(valid_locations) < 2:
		print('Not enough access points (%d)!' % len(valid_locations))
		return jsonify({})
	for valid_location in valid_locations:
		parts = valid_location.split("(")[1].strip(")").split(",")
		info = {}
		info['macAddress'] = parts[3].replace('"', '')
		info['signalStrength'] = int(parts[2])
		info['signalToNoiseRatio'] = int(parts[4])
		access_points.append(info)
	all_info = {'considerIp' : 'false', 'wifiAccessPoints' : access_points}
	r = requests.post(url, json = all_info, params = {'key' : goog_key})
	location = r.json()
	if 'error' not in location:
		location['time'] = time.time()
		location_file = open(location_file_name, 'w')
		pickle.dump(location, location_file)
		location_file.close()
	return jsonify({})

if __name__ == '__main__':
	app.run('0.0.0.0', 80)
