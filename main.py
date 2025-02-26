import datetime
from twilio.rest import Client
import requests
import os
from dotenv import load_dotenv

load_dotenv()

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
API_KEY = os.getenv('API_KEY')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
TWILIO_SID= os.getenv('TWILIO_SID')
TWILIO_PASSWORD = os.getenv('TWILIO_PASSWORD')

params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": API_KEY
}

news_params = {
    'qInTitle': COMPANY_NAME,
    'apiKey': NEWS_API_KEY
}

## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
url = f'https://www.alphavantage.co/query'
r = requests.get(url, params=params)
data = r.json()["Time Series (Daily)"]
data_list = [value for (key, value) in data.items()]
yesterday_data = data_list[0]
yesterday_closing_price = yesterday_data['4. close']

day_before = data_list[1]
day_before_closing_price = day_before['4. close']

difference = float(yesterday_closing_price) - float(day_before_closing_price)
if difference > 0 :
    up_down = '🔺'
else:
    up_down = '🔻'
diff_percent = round((difference / float(yesterday_closing_price)) * 100)

## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.
three_articles = []
if abs(diff_percent) >5:
    new_data = requests.get('https://newsapi.org/v2/everything', params=news_params)
    articles = new_data.json()['articles']
    three_articles = articles[:3]
# print(three_articles)

## STEP 3: Use https://www.twilio.com
# Send a seperate message with the percentage change and each article's title and description to your phone number. 

list_of_articles = [f"{COMPANY_NAME}: {up_down}{diff_percent}%\nHeadline: {article['title']}\nBrief: {article['description']}" for article in three_articles]
client = Client(TWILIO_SID,TWILIO_PASSWORD)

for article in list_of_articles:
    message = client.messages.create(
        body=article,
        from_='yourNumberHere',
        to='recipientNumber'
    )

#Optional: Format the SMS message like this: 
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

