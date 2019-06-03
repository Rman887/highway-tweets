import json
import tweepy

with open('credentials.json', 'r') as f:
    creds = json.load(f)

auth = tweepy.OAuthHandler(creds["CONSUMER_KEY"], creds["CONSUMER_SECRET"])
auth.set_access_token(creds["ACCESS_TOKEN"], creds["ACCESS_SECRET"])

api = tweepy.API(auth, wait_on_rate_limit=True, \
                 wait_on_rate_limit_notify=True, compression=True)


def searchTweets(search="interstate"):
    with open("tweets.json", "w") as f:
        tweets = tweepy.Cursor(api.search, q=search)
        for status in tweets.items(200):
            f.write(str(status._json))
            f.write('\n')


def printTweets():
    with open("tweets.json", "r") as f:
        for line in f:
            try:
                tweetLine = line.strip("'<>() ").replace("\"", chr(17)).replace("'", "\"").replace(chr(17), "'").replace("True", "true").replace("False", "false")
                tweet = eval(line)

                print("ID:", tweet['id'])
                print("Date:", tweet['created_at'])
                print("Contents:", tweet['text'])
                print("User:", tweet['user']['name'], "(@" + tweet['user']['screen_name'] + ")", "ID:", tweet['user']['id'])

                hashtags = []
                for hashtag in tweet['entities']['hashtags']:
                    hashtags.append(hashtag['text'])
                print("Hashtags:", hashtags)

                print()


            except Exception as e:
                print(e)

option = input("1 for search, 2 for print: ")
if option.strip() == "1":
    searchTweets(search=input("Keywords: "))
else:
    printTweets()
