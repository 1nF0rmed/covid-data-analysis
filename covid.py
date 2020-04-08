import requests
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import uuid

URL = "https://api.rootnet.in/covid19-in/unofficial/covid19india.org/statewise"
URL_H = "https://api.rootnet.in/covid19-in/unofficial/covid19india.org/statewise/history"

## FIREBASE setup
cred = credentials.Certificate('covid.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

def load_page():
    page_data = requests.get(url=URL)
    data = page_data.json()
    # Count for country
    total_info = data['data']['total']
    # timestamp
    time = data['lastRefreshed']
    # statewise info
    state_info = data['data']['statewise']

    return total_info,time,state_info

def load_page_history():
    page_data = requests.get(url=URL_H)
    data = page_data.json()

    for day_data in data['data']['history'][len(data['data']['history'])-2:len(data['data']['history'])-1]:
        time = day_data['day']

        for state in day_data['statewise']:
            state['time'] = time
            print(state)
            if updateDB(state['state'], state, "api.rootnet.in") is False:
                break

def updateDB(collection,data,source):
    data['source'] = source
    try:
        db.collection(collection).document().set(data)
    except Exception as e:
        print("[ERR] "+str(e))

        return False

    return True


def loadAndUpdate():
    # Get the required data
    total_info, time, state_info = load_page()
    
    # Update total info to the database
    total_info['time'] = time
    if updateDB("totalInfo", total_info, "api.rootnet.in") is False:
        return

    for state in state_info:
        state['time'] = time
        print(state)
        if updateDB(state['state'], state, "api.rootnet.in") is False:
            break

#load_page_history()
loadAndUpdate()
