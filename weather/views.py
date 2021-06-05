import traceback

from django.shortcuts import render
import requests
import urllib.parse

# url to get the coordinates from location
GET_COORDINATE_URL = 'https://nominatim.openstreetmap.org/search/'
# url for weather details
WEATHER_DETAILS_URL = 'https://api.met.no/weatherapi/locationforecast/2.0/'
# use headers in request
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
}


def get_coordinates(location):
    """
    return the latitude and longitude of the location
    """
    url = (
       GET_COORDINATE_URL + urllib.parse.quote(location) + '?format=json'
    )
    response = requests.get(url).json()[0]
    return response["lat"], response['lon']


# to filter out the data from dict
def get_required_data(data, time='instant'):
    req_data = {}
    time_series_data_list = data.get('properties', {}).get(
        'timeseries', {}
    )
    if time_series_data_list:
        req_data = time_series_data_list[0].get('data', {}).get(time, {}).get('details')
    return req_data


def weather_details(request):
    cxt = {}
    if request.method == 'POST':
        try:
            longitude = request.POST.get('long')
            latitude = request.POST.get('lat')
            if not(latitude and latitude):
                input_location = request.POST.get('loc')
                latitude, longitude = get_coordinates(input_location)

            weather_url = '{url}compact?lat={lat}&lon={long}'.format(
                url=WEATHER_DETAILS_URL, lat=latitude, long=longitude
            )

            response = requests.get(weather_url, headers=HEADERS)
            if response.status_code == 200:
                req_data = get_required_data(
                    eval(response.content)
                )
                cxt['data'] = req_data
                cxt['long'] = longitude
                cxt['lat'] = latitude
            else:
                cxt['err_msg'] = f'API status: {response.status_code}'
        except Exception as e:
            err_msg = f'Something went wrong'
            cxt['err_msg'] = err_msg
    return render(request, 'weather/base.html', cxt)

