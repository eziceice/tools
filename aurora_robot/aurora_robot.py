import slack
import certifi
import ssl as ssl_lib
from slackeventsapi import SlackEventAdapter
from datetime import datetime, timedelta
import calendar
import db_processor

ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
client = slack.WebClient(token='', ssl=ssl_context)
slack_events_adapter = SlackEventAdapter('', endpoint="/slack/events")


def search_result(start, end):
    result = {}
    for item in db_processor.find_date_range(start, end):
        key = item['name']
        if key in result.keys():
            result[key].append(item['date'].date().strftime("%Y-%m-%d"))
        else:
            result[key] = [item['date'].date().strftime("%Y-%m-%d")]
    return result


def process_content(message):
    channel = message['channel']
    key_word = message['text']

    if 'HELP' in key_word.upper():
        client.chat_postMessage(channel=channel,
                                text='Usage: \n 1. Send WFH and @me \n 2. Send REPORT and @me \n 3. Send DATE: YYYY-MM-DD to YYYY-MM-DD and @me \n')

    if 'WFH' in key_word.upper():
        date = datetime.fromtimestamp(float(message['ts']), None)
        name = client.users_info(user=message['user'])['user']['profile']['display_name']
        weekday = calendar.day_name[date.weekday()]
        record = {
            'name': name,
            'date': date
        }
        db_processor.insert(record)
        client.chat_postMessage(channel=channel,
                                text=f"Ok got it, {name} is going to wfh on {weekday} - {date.date()})")

    if 'REPORT' in key_word.upper():
        today = datetime.now().weekday()
        start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=today * 1)
        end = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        result = search_result(start, end)
        client.chat_postMessage(channel=channel, text=result)

    if 'DATE' in key_word.upper():
        tmp_date = key_word.split(':')[1].split('to')
        start = datetime.strptime(tmp_date[0].strip(), '%Y-%m-%d')
        end = datetime.strptime(tmp_date[1].strip(), '%Y-%m-%d')
        result = search_result(start, end)
        client.chat_postMessage(channel=channel, text=result)


@slack_events_adapter.on('app_mention')
def message_mentioned(event_data):
    message = event_data['event']
    process_content(message)


slack_events_adapter.start(port=3000)
