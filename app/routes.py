import atexit
import xml.etree.ElementTree as ET
import jsonpickle
import requests

from app import app
from math import acos, cos, radians, sin
from flask import render_template
from flask import request
from flask import abort
from app.models import Station
from app.models import Price
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

def download_files():
    print('downloading file')
    url = 'https://publicacionexterna.azurewebsites.net/publicaciones/prices'
    r = requests.get(url)
    with open('/static/prices.xml', 'wb') as f:
        f.write(r.content)
    print('file downloaded')
    print('downloading file')
    url = 'https://publicacionexterna.azurewebsites.net/publicaciones/places'
    r = requests.get(url)
    with open('/static/places.xml', 'wb') as f:
        f.write(r.content)
    print('file downloaded')

scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    func=download_files,
    trigger=IntervalTrigger(minutes=60),
    id='downloading_job',
    name='Download files every hour',
    replace_existing=True)
download_files()
# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')
@app.route('/80430b0bd02771d3036d126bf1d460c4', methods=['GET',])
def getStations():

    if request.args.get('lat') == None or request.args.get('lng') == None or request.args.get('dst') == None:
        abort(400)

    # get query string params
    lat = float(request.args.get('lat'))
    lng = float(request.args.get('lng'))
    dst = float(request.args.get('dst'))

    places_id = list()
    stations = list()

    places_tree = ET.parse('static/places.xml')
    places = places_tree.getroot()
    for place in places:
        data = place.find('location')
        #for data in place.findall('location'):
        x = float(data.find('x').text)
        y = float(data.find('y').text)
        formula = ( 6371 * acos( cos( radians( y ) ) * cos( radians( lat ) ) * cos( radians( lng ) - radians( x ) ) + sin( radians( y ) ) * sin( radians( lat ) ) ) )
        if (formula < dst):
            s = Station()
            s.place_id = place.get('place_id')
            s.name = place.find('name').text
            s.brand = place.find('brand').text
            s.cre_id = place.find('cre_id').text
            s.category = place.find('category').text
            s.address = data.find('address_street').text
            s.lat = y
            s.lng = x
            stations.append(s)
            places_id.append(place.attrib)

    prices_tree = ET.parse('static/prices.xml')
    prices = prices_tree.getroot()
    for price in prices:
        if price.attrib in places_id:
            s_i = places_id.index(price.attrib)
            for p in price.findall('gas_price'):
                po = Price()
                po.type = p.get('type')
                po.price = p.text
                stations[s_i].prices.append(po)
    response = app.response_class(
        response=jsonpickle.encode(stations, unpicklable=False),
        status=200,
        mimetype='application/json'
    )
    return response
