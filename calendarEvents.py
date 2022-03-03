from asyncio import events
import os
from bs4 import BeautifulSoup
import logging
import requests
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(filename="output.log", level=logging.INFO, format='%(levelname)s - %(asctime)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p') #Logger

urlCodes = {
	'CSCI251' : '31987',
	'MATH221' : '32052',
	'CSIT214' : '32067'
}

payload = {
	# 'anchor' : 'index.php',
	'username' : os.getenv("USERNAME"),
	'password' : os.getenv("PASS"),
	'logintoken' : ''
}

MOODLE_HOME = 'https://moodle.uowplatform.edu.au/login/'

headers = {
	'Host': 'moodle.uowplatform.edu.au',
	'Connection': 'close',
	'Content-Length': '134',
	'Cache-Control': 'max-age=0',
	'sec-ch-ua': '"Chromium";v="89", ";Not A Brand";v="99"',
	'sec-ch-ua-mobile': '?0',
	'Upgrade-Insecure-Requests': '1',
	'Origin': 'https://moodle.uowplatform.edu.au',
	'Content-Type': 'application/x-www-form-urlencoded',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
	'Sec-Fetch-Site': 'same-origin',
	'Sec-Fetch-Mode': 'navigate',
	'Sec-Fetch-User': '?1',
	'Sec-Fetch-Dest': 'document',
	'Referer': 'https://moodle.uowplatform.edu.au/login/index.php',
	'Accept-Encoding': 'gzip, deflate',
	'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8'
}

proxies = {
	"http" : "http://127.0.0.1:8080"
}

def login():
    '''Logs into moodle and returns session'''

    # Login
    session = requests.session()

    r = session.get(MOODLE_HOME)
    soup = BeautifulSoup(r.content, 'html.parser')

    # get csrf token
    logintoken = soup.find('input', attrs={'name' : 'logintoken'})['value']
    payload['logintoken'] = str(logintoken)

    r = session.post(MOODLE_HOME, data= payload)

    if r.status_code != 200:
        logging.critical(f"An error occured while trying to log in. Server returned status cod {r.status_code}")
        exit()

    print(payload)
    # with open('index.html', 'w') as f:
    #     f.writelines(str(r.text))

    logging.info(f"Successfully logged in as {payload['username']}")
    return session

def getEvents(urlCode, session):

    """Get calendar events from moodle and returns array of json events"""

    r = session.get(f'https://moodle.uowplatform.edu.au/calendar/view.php?view=upcoming&course={urlCode}', data=payload)
    
    if r.status_code != 200:
        logging.error(f"Server returned bad status when requesting events, status {r.status_code}")
        
    soup = BeautifulSoup(r.content, 'html.parser')

    with open('index.html', 'w') as f:
        f.writelines(str(r.text))

	# get events for subject
    event_list = soup.find('div', attrs={'class': 'eventlist my-1'})
    if event_list == None:
        logging.info("No events found, returning...")
        return {}

    events = event_list.find_all('div', attrs={'class' : 'card rounded'})

    event_list = []
    for event in events:
        
        title = event.find('h3', attrs= {'class': 'name d-inline-block'}).text
        time = event.find('div', attrs={'class': 'col-11'}).text
        event_type = getType(title)

        event_list.append(
            {
                'title':title,
                'time':time,
                'classification': event_type
            }
        )

    return event_list

def getType(title):

    """Finds type of event and return string of event type"""

    title = title.lower()

    if 'lab' in title:
        return 'Labs/Study'
    elif 'assignment' in title or 'quiz' in title:
        return 'Assignments'

    return 'Labs/Study'
    # Special rules specific for subject
    # if 'F2F (Due date)' in title:# Specific rule for CSIT214 group project
    #     return 'lab'


def get_all():
    
    logging.info("Events requested for all subjects")
    
    session = login() # Get session for user

    subjects = [] # Array of subject classes
    for key, value in urlCodes.items():
        
        logging.info(f"Getting events for {key} with url code {value}")
        subject = {
            'subject_code':key,
            'url_code':value,
            'events': getEvents(urlCode=value,session=session)
        }

        subjects.append(subject)

    return subjects

def get_subject(sub_code):
    
    logging.info(f"Events request for subject {sub_code}")

    session = login() # Get session for user

    try:
        subject = {
            'subject_code':sub_code,
            'url_code':urlCodes[sub_code],
            'events': getEvents(urlCode=urlCodes[sub_code], session=session)
        }
    except KeyError:
        logging.critical("Invalid subject code provided")
        return {'error':'Invalid subject code'}
    
    logging.info(f"Returning subject")
    return subject

if __name__ == "__main__":
    print(get_subject('CSCI251'))
