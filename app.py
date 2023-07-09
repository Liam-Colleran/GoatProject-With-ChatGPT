from flask import Flask, render_template, request, jsonify
import requests
import json
import math
from contextlib import suppress

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    query = data['query']
    numberOfShoes = data['numberOfShoes']

    pages = math.ceil(numberOfShoes / 19) + 1
    result = []

    for i in range(1, pages):
        output, shoelist = perform_search(query, i)
        if numberOfShoes > 19:
            result.extend(get_info(shoelist))
            numberOfShoes -= 19
        else:
            result.extend(get_info(shoelist, numberOfShoes))
            break

    return jsonify({'shoes': result})

def perform_search(query, page=1):
    url = f'https://ac.cnstrc.com/search/{query.replace(" ", "%20")}?c=ciojs-client-2.35.2&key=key_XT7bjdbvjgECO5d8&i=dd315c3b-ef56-4b02-bcb0-c565b44efd01&s=8&page={page}'
    html = requests.get(url=url)
    output = json.loads(html.text)
    shoelist = output['response']['results']
    return output, shoelist

def info_or_NA(container):
    try:
        result = container
    except KeyError:
        result = 'Data Not Found.'
    return result

def get_info(shoelist, repeat_amount=19):
    result = []
    for i in range(repeat_amount):
        try:
            shoelist[i]
        except IndexError:
            print('Number of shoes searched exceeds the number of listings.')
            break
        
        with suppress(KeyError):
            name = info_or_NA(shoelist[i]['value'])
            image = info_or_NA(shoelist[i]['data']['image_url'])
            condition = info_or_NA(shoelist[i]['data']['product_condition'].replace('_', ' '))
            retail_price = info_or_NA(shoelist[i]['data']['retail_price_cents'] / 100)
            release = info_or_NA(shoelist[i]['data']['release_date_year'])

        shoe_info = {
            'name': name,
            'image': image,
            'condition': condition,
            'retailPrice': retail_price,
            'release': release
        }

        result.append(shoe_info)

    return result

if __name__ == '__main__':
    app.run()
