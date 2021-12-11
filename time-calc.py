"""
Given a calendar, categorize all events based on keyword patterns 
and produce a report that shows how much time I am spending on each
category in a given week. 
1. Set up google app, calendar API scope, boilerplate, and O-auth connection //
2. Get all events in the current week, in an array //
3. Specify keyword patterns needed for each category
4. If event's title match a keyword pattern, add to a category dedicated array
5. Calculate total time for each category dedicated array
6. Print results
"""

from __future__ import print_function
import datetime
import pendulum

from datetime import date, timedelta
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    # today = datetime.datetime.today()
    # start_week = str(today - timedelta(days=today.weekday()))
    # end_week = str(start_week + timedelta(days=6))
    today = pendulum.now()
    start_week = today.start_of('week')
    end_week = today.end_of('week')

    events_result_primary = service.events().list(calendarId='primary', timeMin=start_week, 
                                        timeMax = end_week, singleEvents = True).execute()
    events_result_secondary = service.events().list(calendarId='michael@lemontreemedia.io', 
                                        timeMin= start_week, 
                                        timeMax = end_week, singleEvents = True).execute()
    events_primary = events_result_primary.get('items', [])
    events_secondary = events_result_secondary.get('items', [])
    tmp_arr = events_primary + events_secondary

    # all events within the current week
    event_final_results = []

    for event in tmp_arr:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        if event['start'].get('dateTime') == None:
            continue
        # print(start, '<-->', end, event['summary'])
        event_final_results.append(event)

    # set keyword patterns
    patterns = {'CV': 'Computer Vision', 'BCI': 'Brain Computer Interface', 
                'UI': 'User Interface Design', 'AR': 'Topics in Computer Science', 
                'MH': 'Masterpieces of Western Music', 'Reading': 'Reading', 
                'apply': 'Job', 'Coding': 'Coding', 'LT': 'LemonTree', 
                'Sports': 'Sports', '***': 'Chill Time'}

    patterns_arr = {}
    for i in patterns:
        patterns_arr[i] = []
    category_duration = {}
    for i in patterns:
        category_duration[i] = 0 

    # for each keyword, search all events of the week. If there's a match, add to patterns_arr
    # for each category, calculate sum of all event's duration and rounded to hours
    for item in event_final_results:
        title = str(item['summary'].lower())
        for key in patterns:
            title_slice = title[:len(key)]        
            if patterns[key].lower() in title:
                patterns_arr[key].append(item)
                duration = calculate_time(item)
                prev_duration = category_duration[key] 
                category_duration[key] =  prev_duration + duration
            elif title_slice == key.lower():
                patterns_arr[key].append(item)
                duration = calculate_time(item)
                prev_duration = category_duration[key] 
                category_duration[key] =  prev_duration + duration
            # elif title.lower() == 'breakfast' or title.lower() == 'lunch' or title.lower() == 'dinner':
            #     patterns_arr['Meals'].append(item)
            #     duration = calculate_time(item)
            #     prev_duration = category_duration[key] 
            #     category_duration['Others'] =  prev_duration + duration
            # else:
            #     patterns_arr['Others'].append(item)
            #     duration = calculate_time(item)
            #     prev_duration = category_duration[key] 
            #     category_duration['Others'] =  prev_duration + duration

    # for i in patterns_arr:
    #     print(i, patterns_arr[i], '\n')

    patterns_expected_hours = {'CV': '20', 'BCI': '15', 
                'UI': '10', 'AR': '10', 
                'MH': '4', 'Reading': '3', 
                'apply': '3', 'Coding': '12', 'LT': '3', 
                'Sports': '3', '***': '11'}

    # print the result
    for i in category_duration:
        print(patterns[i], ": ", round(category_duration[i],1), " hour(s), expected ", patterns_expected_hours[i], " hour(s)\n")

    school_hours = category_duration['CV'] + category_duration['BCI'] + category_duration['AR'] + \
            category_duration['MH'] + category_duration['UI']
    total_hours = 0
    for i in event_final_results:
        total_hours+=calculate_time(i)
    print('Coursework total: ', round(school_hours,1))   
    
    #Create an all-day summary event for Sunday, summarizing activity time

def calculate_time(event):
    start = event['start'].get('dateTime')[:-6]
    end = event['end'].get('dateTime')[:-6]
    start_object = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")
    end_object = datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%S")
    duration = end_object - start_object
    duration_in_s = duration.total_seconds()
    minutes = divmod(duration_in_s, 60)[0] 
    hours = round(minutes/60, 1)
    return hours

if __name__ == '__main__':
    main()

