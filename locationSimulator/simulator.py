#!/usr/bin/env python
import pika, sys, os, json
import googlemaps, time

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
    coordinates = get_route_coordinates(api_key, start, end)
    coordinates.append({'latitude': 0, 'longitude': 0})
    print(coordinates)
    while(len(coordinates) > 0):
        channel.basic_publish(exchange='', routing_key='queue2', body=json.dumps(coordinates.pop(0)))
        time.sleep(updateFrequency)


def get_route_coordinates(api_key, start_point, end_point):
    gmaps = googlemaps.Client(key=api_key)

    # Dobijanje rute između početne i krajnje tačke
    directions_result = gmaps.directions(start_point, end_point, mode="driving")

    # Izvlačenje koordinata iz dobijenih koraka rute
    coordinates = []
    for step in directions_result[0]['legs'][0]['steps']:
        coordinates.append({
            'latitude': step['start_location']['lat'],
            'longitude': step['start_location']['lng']
        })

    # Dodajte krajnju tačku
    coordinates.append({
        'latitude': directions_result[0]['legs'][0]['end_location']['lat'],
        'longitude': directions_result[0]['legs'][0]['end_location']['lng']
    })

    return coordinates





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