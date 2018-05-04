# Returns the forecast, news, and calendar events by parsing through html and
# using google API

from __future__ import print_function
import requests
from bs4 import BeautifulSoup
from newspaper import fulltext
import newspaper
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import datetime
import logging


# Returns a dictionary mapping periods of time to their weather
def returnForecast():
    
    forecast = {}
    
    # Sometimes the website is down and causes errors
    try:
        
        page =  requests.get("https://forecast.weather.gov/MapClick.php?x=212&y=" + 
                "132&site=pbz&zmx=&zmy=&map_x=212&map_y=132#.WtfexYjwbD4")
        soup = BeautifulSoup(page.content, "html.parser")
        sevenDay = soup.find(id="seven-day-forecast")
        
        # Finds all the periods/days listed with information on the website
        periodTags = sevenDay.select(".tombstone-container .period-name")
        periods = [pt.get_text() for pt in periodTags]
        
        # Finds descriptions of the weather and the temp for each period on the webiste
        shortDescs = [sd.get_text() for sd in sevenDay.select(".tombstone-container .short-desc")]
        temps = [t.get_text() for t in sevenDay.select(".tombstone-container .temp")]
        descs = [d["title"] for d in sevenDay.select(".tombstone-container img")]
        
        # Puts each day in the dictionary mapping to its weather and temp
        for item in periods:
            for i in range(len(periods)):
                if item == periods[i]:
                    forecast[item] = [shortDescs[i], temps[i], descs[i]]
        
        # Adds current temperature to the dictionary as well
        current = soup.find(id="current_conditions-summary")
        currTemp = current.find(class_="myforecast-current-lrg").get_text()
        forecast["Temp"] = currTemp
        
    except:
        
        return {}
        
    return forecast


"""followed this documentation to use newspaper module to get headlines
   http://newspaper.readthedocs.io/en/latest/"""
   
# Returns a list of news headlines
def returnNews():
    
    news = {}
    
    # Parses through the google news headlines
    page = newspaper.build("https://news.google.com/news/?ned=us&gl=US&hl=en")
    
    for article in page.articles:
        try:
            url = article.url
            html = requests.get(url).text
            text = fulltext(html)
            # Creates a dictionary mappying titles to full text
            if article.title != None:
                news[article.title] = text
        except:
            pass
    return news
 
"""followed this tutorial to use the google api to extract calendar events
   https://developers.google.com/calendar/quickstart/python"""
 
# Returns a list of calendar events
def returnCalendar():
    
    calendar = []
    
    # Setup the Calendar API
    SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
    store = file.Storage('credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()), cache_discovery=False)
    
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=5, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    
    if not events:
        events = ['No upcoming events found.']
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        #print(start, event['summary'])
        calendar.append((start, event['summary']))
    return calendar
        