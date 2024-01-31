#!/usr/bin/env python
import pika, sys, os, json
import googlemaps, time

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='queue1')
    channel.queue_declare(queue='queue2')

    def callback(ch, method, properties, body):
        json_data = json.loads(body.decode('utf-8'))
        start = tuple(json_data["start"])
        end = tuple(json_data["end"])
        print(start, end)
        send_to_map(start, end, channel)

    channel.basic_consume(queue='queue1', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


def send_to_map(start, end, channel):
    api_key = 'AIzaSyALYenrDpiEz0dpZw4QefuAVK0elrLFWMA'
    coordinates = get_route_coordinates(api_key, start, end)
    print(coordinates)
    while(len(coordinates) > 0):
        channel.basic_publish(exchange='', routing_key='queue2', body=json.dumps(coordinates.pop()))
        time.sleep(1)
    


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
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)