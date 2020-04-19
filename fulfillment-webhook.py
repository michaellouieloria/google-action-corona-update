import requests
import inflection
from bs4 import BeautifulSoup
from flask import Flask, request, make_response, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    req = request.get_json(force=True)

    # fetch action from json
    action = req.get('queryResult').get('action')
    case_value = req.get('queryResult').get('parameters').get('cases')
    country_value = req.get('queryResult').get('parameters').get('country')
    speak_output = "Sorry, I had trouble doing what you asked. Please try again."

    if (country_value and case_value and (action == 'get_cases')):
        country_value = {
            'usa': 'us',
            'united states': 'us',
            'united states of america': 'us',
            'united kingdom': 'uk',
            'uae': 'united-arab-emirates',
            'ivory coast': 'cote-d-ivoire',
            'palestine': 'state-of-palestine',
            'congo': 'democratic-republic-of-the-congo',
            'vietnam': 'viet-nam',
        }.get(country_value.lower(), country_value)

        if case_value in ['deaths', 'death', 'recovered', 'recovering', 'recover', 'confirmed', 'confirming', 'confirm']:
            try:
                if country_value == 'worldwide':
                    response = requests.get("https://www.worldometers.info/coronavirus")
                else:
                    response = requests.get("https://www.worldometers.info/coronavirus/country/{}".format(inflection.dasherize(country_value.lower())))

                soup = BeautifulSoup(response.text, 'html.parser')
                figures = soup.find_all('div', id='maincounter-wrap')

                if case_value in ['confirmed', 'confirming', 'confirm']:
                    confirmed = figures[0].find('span').text
                    speak_output = "{} confirmed cases".format(confirmed)

                if case_value in ['deaths', 'death']:
                    deaths = figures[1].find('span').text
                    speak_output = "{} deaths".format(deaths)

                if case_value in ['recovered', 'recovering', 'recover']:
                    recovered = figures[2].find('span').text
                    speak_output = "{} recovered cases".format(recovered)

            except:
                speak_output = "Sorry, I had trouble doing what you asked. Please try again."

    response = {'fulfillmentText': speak_output}
    return make_response(jsonify(response))
