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

## TODO -- 1) search only for hashtags in English

# To login to my bot's twitter account

class MyStreamListener(tweepy.StreamListener):
    # override tweepy.StreamListener to add logic to on_status
    def on_status(self, status):
        print(status.text)

        # Emojis can't be encoded into .txt file, so only accept tweets without them
        try :
            status.text.encode('utf-8','strict')
            file = open('tweets.txt', 'a')
            file.write(status.text + '\n')
        except UnicodeError :
            print('Tweet contained non UTF-8 chars; deleted.')





def authenticate_twitter() :
    print('Authenticating twitter account...')

    consumer_key = 'is secret shh'
    consumer_secret = 'is secret shh'
    access_token = 'is secret shh'
    access_token_secret = 'is secret shh'
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


def generate_message(chain, trendsNames) :

    i = random.randint(0, len(trendsNames))
    char_limit = 140 - (len(trendsNames[i])+5)

    # The first word will be a random key from the Markov chain
    word1 = random.choice(list(chain.keys()))

    # The message will initially be just the chosen word, but capitalized
    message = word1.capitalize()

    while len(message) < char_limit :
        word2 = random.choice(chain[word1])
        word1 = word2
        message += ' ' + word2

    # add a random trending hashtag to the end of the tweet
    message += ' ' + trendsNames[i]

    # Sometimes, an emoji in twitter isn't detected by the emoji filter when the tweets all first compile.
    # It appears in the message as '&amp'... so let's take care of it
    print(len(message))
    if '&amp' in message or len(message) > 140:
        generate_message(chain, trendsNames)

    return message


def run_bot(twitter) :
    open('tweets.txt', 'w').close()

    # Get the current trending topics from twitter

    # trends_place() returns a json object, but tweepy deserializes it for us. trends will be an ordinary Python list
    trends1 = twitter.trends_place(1)

    # trends is a list with only one element, a dict which will be put in trends_dict
    trends_dict = trends1[0]

    # grab the trends
    trends = trends_dict['trends']

    #trendsNames = []
    # grab the name of each trend (only hashtags, not people)
    trendsNames = [trend['name'] for trend in trends if trend['name'][0] == '#']
    #for trend in trends :
        #if trend['name'][0] == '#' :
            #try :
                #trendsNames.append(trend['name'].encode('ascii', 'strict'))
            #except UnicodeError :
                #print('Hashtag is not in English; discarded.')

    print(trendsNames)
    # Go through a large amount of tweets from all users using a stream listener

    # ---------- STREAMING METHOD ------------ #

    my_stream_listener = MyStreamListener()
    my_stream = tweepy.Stream(auth = twitter.auth, listener = my_stream_listener)

    # streams all tweets with trending hashtags send out by U.S. accounts
    my_stream.filter(track=trendsNames, async=True, locations=[-169.90, 52.72, -130.53, 72.40,
                                                                        -160.6, 18.7, -154.5, 22.3,
                                                                        -124.90, 23.92, -66.37, 50.08])

    # However many seconds the program sleeps will determine how long the stream continues for
    time.sleep(60)
    my_stream.disconnect()

    tweets = ''

    with open('tweets.txt', 'r') as file :
        tweets = file.read()

    print(tweets)

    # Generate the Markov chain
    chain = generate_chain(tweets)


    # Generate the message using the chain
    message = generate_message(chain, trendsNames)

    print('The Markov chain: ' + message)

    # Tweet out the resulting Markov chain!

    twitter.update_status(message)

    print('Sleeping for one hour...')
    # Bot will tweet once every hour (3,600 seconds)
    time.sleep(60*20)

twitter = authenticate_twitter()

while True :
    run_bot(twitter)


