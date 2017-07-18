# Markov Twitter Bot

# This bot will imitate a Twitter user. To do this, it will look at discussions around trending hashtags, create a
# Markov chain based on those discussions, then send out various (semi-coherent) tweets based on the Markov chain.

import tweepy
import time
import os
import random

# Four basic steps to the program
# 1) Read the source text
# 2) Build the Markov chain
# 3) Use the Markov Chain to generate a random phrase
# 4) Output the phrase

## TODO -- 1) get twitter stream working, and 2) use it to find all the tweets w/ trending hashtags

# To login to my bot's twitter account
class MyStreamListener(tweepy.StreamListener):
    # override tweepy.StreamListener to add logic to on_status
    def on_status(self, status):
        print(status.text)

def authenticate_twitter() :
    print('Authenticating twitter account...')

    consumer_key = 'icRe9PnxhbXzAfeWxBhjNFdTN'
    consumer_secret = 'wHULrdZE0ELoHMs0ySmwT41OHe0d2TlHemibcVi8GCuoPpF4Lu'
    access_token = '701887784303198208-NvPpwavnDqoylOijP8XYOFFXrpYD2Kk'
    access_token_secret = 'BCkL7jhWH1e0y4weUEKNQd0CIWT4px1xp54sz5juWW6qV'
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    twitter = tweepy.API(auth)

    print('Authenticated as xbilboxswaggins')

    return twitter

# To generate the Markov chain

def generate_chain(text, chain={}) :
    words = text.split(' ')

    # Index should be 1, because the first word will be the key, and the subsequent word (at index 1) will be the value
    # You'll see what I mean...
    index = 1

    for word in words[index:] :

        # The first word is a key
        key = words[index-1]

        # If a word's key (the previous word) is already in the chain, make the current word the key's value
        if key in chain :
            chain[key].append(word)
        else :
            chain[key] = [word]

        index += 1

    return chain

# To generate the message
# Character limit of twitter is 140

def generate_message(chain, char_limit=140) :

    # The first word will be a random key from the Markov chain
    word1 = random.choice(list(chain.keys()))

    # The message will initially be just the chosen word, but capitalized
    message = word1.capitalize()

    while len(message) < char_limit :
        word2 = random.choice(chain[word1])
        word1 = word2
        message += ' ' + word2

    return message

def run_bot(twitter) :

    contents = ''

    ## Get the current trending topics from twitter

    # trends_place() returns a json object, but tweepy deserializes it for us. trends will be an ordinary Python list
    trends1 = twitter.trends_place(1)

    # trends is a list with only one element, a dict which will be put in trends_dict
    trends_dict = trends1[0]

    # grab the trends
    trends = trends_dict['trends']

    # grab the name of each trend (only hashtags, not people)
    names = [trend['name'] for trend in trends if trend['name'][0] == '#']

    # put all the names together into a list
    trendsNames = ' '.join(names).split(' ')


    ## Go through a large amount of tweets from all users using a stream listener

    my_stream_listener = MyStreamListener()
    my_stream = tweepy.Stream(auth = twitter.auth, listener = my_stream_listener)




    # Generate the Markov chain
    # chain = generate_chain(contents)

    # Generate the message using the chain
    # message = generate_message(chain)

    # print('The Markov chain: ' + message)

    print(trendsNames)

    # Bot will tweet once every hour (3,600 seconds)
    time.sleep(10)

twitter = authenticate_twitter()

while True :
    run_bot(twitter)


