# bot.py
# Thomas Killian
# 7/14/21

import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter

env_path = Path('.')/'.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'],'/slack/events',app)

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
BOT_ID = client.api_call("auth.test")['user_id']
#client.chat_postMessage(channel='#general', text="Hello World!")

message_counts = {}

@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event',{})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')
    if BOT_ID is not user_id:
        if user_id in message_counts:
            message_counts[user_id] += 1
        else:
            message_counts[user_id] = 1
        #client.chat_postMessage(channel=channel_id, text=text)

@app.route('/usage', methods=['POST'])
def usage():
    data=request.form
    channel_id = data.get('channel_id')
    
    response = "Slack Bot Current Commands:\n all commands are slash commands (/command)\n \
        bodule: puts the B emoji in front of whatever you type next (/bodule hello -> Bello\n \
        mockery: mocks the following text to upper and lower case\n \
        claps: puts the clap emoji between each word like you're fighting/yelling"

    client.chat_postMessage(channel=channel_id, text=response)

    return Response(), 200

@app.route('/claps', methods=['POST'])
def claps():
    data = request.form
    channel_id = data.get('channel_id')
    text = data.get('text')

    #phrase = text.rstrip().split()
    response =''

    for letter in text:
        if letter == ' ':
            letter = ' 👏 '
        response += letter
    client.chat_postMessage(channel=channel_id, text=response)

    return Response(), 200

@app.route('/bodule', methods=['POST'])
def bodule():
    data = request.form
    channel_id = data.get('channel_id')
    text = data.get('text')
    
    phrase = text.rstrip().split()
    response = ''
    vowels={'a','e','i','o','u'}

    for word in phrase:
        current = word[0].lower()

        if current in vowels:
            response += ' 🅱️' + word
        else:
            response += ' 🅱️' + word[1:]

    client.chat_postMessage(channel=channel_id, text=response)
    return Response(), 200

@app.route('/mockery', methods=['POST'])
def mockery():
    data = request.form
    channel_id = data.get('channel_id')
    text = data.get('text')

    phrase = text.lower().rstrip()
    response = ''

    for count, letter in enumerate(phrase):
        if count % 2:
            letter = letter.upper()
        response += letter

    client.chat_postMessage(channel=channel_id, text=response)
    return Response(), 200


@app.route('/message-count', methods=['POST'])
def message_count():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    message_count = message_counts.get(user_id, 0)

    client.chat_postMessage(channel=channel_id, text=f"Messages: {message_count}")
    return Response(), 200

if __name__ == "__main__":
    app.run(debug=True)
