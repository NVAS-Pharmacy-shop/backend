#!/usr/bin/env python
import pika, sys, os, json
import requests, time, polyline

def main():
    while True:
        method_frame, header_frame, body = channel.basic_get('queue1')
        if method_frame:
            callback(channel, method_frame, header_frame, body)
            channel.basic_ack(method_frame.delivery_tag)
        else:
            time.sleep(1)

def callback(ch, method, properties, body):
        json_data = json.loads(body.decode('utf-8'))
        start = tuple(json_data["start"])
        end = tuple(json_data["end"])
        updateFrequency = int(json_data["updateFrequency"])
        print(start, end)
        #print("Update frequency: ", updateFrequency)
        send_to_map(start, end, channel, updateFrequency)


def send_to_map(start, end, channel, updateFrequency):
    api_key = 'AIzaSyALYenrDpiEz0dpZw4QefuAVK0elrLFWMA'

    # Google Maps Directions API endpoint
    api_endpoint = 'https://maps.googleapis.com/maps/api/directions/json?'
    request_url = f'{api_endpoint}origin={start[0]},{start[1]}&destination={end[0]},{end[1]}&key={api_key}&overview_polyline=true'
    coordinates = get_route_coordinates(request_url)
 
    coordinates.append((0, 0))

    print(coordinates)
    coordinate = coordinates.pop(0)
    coordinate_dict = {"latitude": coordinate[0], "longitude": coordinate[1]}
    channel.basic_publish(exchange='', routing_key='queue2', body=json.dumps(coordinate_dict))
    time.sleep(updateFrequency)
    while(len(coordinates) > 0):
        popCount = updateFrequency*2
        while (popCount > 0 and len(coordinates) > 2):
            coordinates.pop(0)
            popCount -= 1
        coordinate = coordinates.pop(0)
        coordinate_dict = {"latitude": coordinate[0], "longitude": coordinate[1]}
        channel.basic_publish(exchange='', routing_key='queue2', body=json.dumps(coordinate_dict))
        time.sleep(updateFrequency)


def get_route_coordinates(request_url):
    #print(request_url)
    response = requests.get(request_url)

    #print("request:", request_url)

    # Dobijanje rute između početne i krajnje tačke
    if response.status_code == 200:
        # Parse the response JSON
        data = response.json()

        #print(data)
        # Extract the 'overview_polyline'
        overview_polyline = data.get('routes', [{}])[0].get('overview_polyline', {}).get('points', '')

        decoded_coordinates = polyline.decode(overview_polyline)

        # Return the 'overview_polyline'
        return decoded_coordinates
    else:
        print(f'Error {response.status_code}: {response.text}')

   





if __name__ == '__main__':
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        channel.queue_declare(queue='queue1')
        channel.queue_declare(queue='queue2')
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)