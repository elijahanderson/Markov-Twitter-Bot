# Markov Twitter Bot

# This bot will imitate a Twitter user. To do this, it will look at discussions around trending hashtags, create a
# Markov chain based on those discussions, then send out various (semi-coherent) tweets based on the Markov chain.

import tweepy
import time
import random
import langid
import language_check

# Four basic steps to the program
# 1) Read the source text
# 2) Build the Markov chain
# 3) Use the Markov Chain to generate a random phrase
# 4) Output the phrase

# To login to my bot's twitter account


class MyStreamListener(tweepy.StreamListener):

    # override tweepy.StreamListener to add logic to on_status
    def on_status(self, status):

        print(status.text)

        # Emojis can't be encoded into .txt file, so only accept tweets without them
        try :
            status.text.encode('utf-8', 'strict')
            file = open('tweets.txt', 'a')
            file.write(status.text + '\n')

        except UnicodeError :
            print('Tweet contained non UTF-8 chars; discarded.')


# To "log in" to bot's twitter account


def authenticate_twitter() :
    print('Authenticating twitter account...')

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    twitter = tweepy.API(auth)

    print('Authenticated.')

    return twitter


# To generate the Markov chain


def generate_chain(text, chain={}) :

    words = text.split(' ')

    # Index should be 1, because the first word will be the key, and the subsequent word (at index 1) will be the value
    # You'll see what I mean...
    index = 1

    for word_value in words[index:] :

        # The first word is a key
        key = words[index-1]

        # If a word's key (the previous word) is already in the chain, make the current word the key's value
        if key in chain :
            chain[key].append(word_value)

        else :
            chain[key] = [word_value]

        index += 1

    return chain


# To generate the message
# Character limit of twitter is 140


def generate_message(chain, chosen_trend) :

    char_limit = 140 - (len(chosen_trend)+5)

    # The first word will be a random key from the Markov chain
    word1 = random.choice(list(chain.keys()))

    # The message will initially be just the chosen word, but capitalized
    message = word1.capitalize()

    # while the length of message doesn't exceed 140 chars, keep adding words that follow the Markov chain
    while len(message) < char_limit :
        word2 = random.choice(chain[word1])

        # check if the words are English
        if is_english(word2) :
            word1 = word2
            message += ' ' + word2

        else :
            # if is_english() keeps returning false because a non-English word only has one value,
            # assign a different key to word1
            word1 = random.choice(list(chain.keys()))

        print(message)

    # add the chosen trend to the end of the tweet
    message += ' ' + chosen_trend

    # Fix any grammatical errors if possible (Also occasionally fixes some foreign words)
    tool = language_check.LanguageTool('en-US')
    matches = tool.check(message)
    message = language_check.correct(message, matches)
    print('Grammarized message: ' + message)

    # Sometimes, an emoji in twitter isn't detected by the emoji filter when the tweets all first compile.
    # It appears in the message as '&amp'... so call generate_message() again until there isn't one in there
    print('Message length: ' + len(message))

    if '&amp' in message or len(message) > 140:
        return generate_message(chain, chosen_trend)

    else :
        return message


# To test if the trends are in ASCII-only chars (filters out some foreign trends)


def is_ascii(trend) :
    return all(ord(c) < 128 for c in trend)


# To test if the words in the final message are in English


def is_english(word) :

    print('Checking language of \'' + word + '\'...')
    print(langid.classify(word))

    if langid.classify(word)[0] == 'en':
        print('English!')
        return True

    else:
        print('Not English...')
        return False


def run_bot(twitter) :

    # Clear any tweets that have been stored in the past
    open('tweets.txt', 'w').close()

    # Get the current trending topics from twitter
    #
    # trends_place() returns a json object, but tweepy deserializes it for us. trends will be an ordinary Python list
    trends1 = twitter.trends_place(1)

    # trends1 is a list with only one element, a dict which will be put in trends_dict
    trends_dict = trends1[0]

    # grab the trends
    trends = trends_dict['trends']

    # grab the name of each trend (only hashtags, not people)
    names = [trend['name'] for trend in trends if trend['name'][0] == '#' and is_ascii(trend['name'])]

    print('\nThe trending hashtags: \n')
    print(names)

    # Go through a large amount of tweets from all users using a stream listener ######################
    #                                                                                                 #
    # ----------------------------------- STREAMING METHOD ------------------------------------------ #
    #                                                                                                 #
    # although there are several trending hashtags, the bot will choose one and use all of the tweets #
    # that include it                                                                                 #
    ###################################################################################################

    # get a random trending hashtag
    i = random.randint(0, len(names) - 1)
    chosen_trend = names[i]

    print('\n***************\n\nThe bot will imitate tweets concerning ' + chosen_trend + '\n\n***************\n')

    my_stream_listener = MyStreamListener()
    my_stream = tweepy.Stream(auth = twitter.auth, listener = my_stream_listener)

    # streams all tweets with trending hashtags send out by U.S. accounts
    my_stream.filter(track=chosen_trend, async=True, locations=[-169.90, 52.72, -130.53, 72.40,
                                                         -160.6, 18.7, -154.5, 22.3,
                                                         -124.90, 23.92, -66.37, 50.08])

    # However many seconds the program sleeps will determine how long the stream continues for
    # I use five minutes to get a TON of tweets, so I can build a good chain
    time.sleep(60*5)
    my_stream.disconnect()

    tweets = ''

    with open('tweets.txt', 'r') as file :
        tweets = file.read()

    # Generate the Markov chain
    chain = generate_chain(tweets)

    # Generate the message using the chain
    message = generate_message(chain, chosen_trend)

    print('The Markov chain: ' + message)

    # Tweet out the resulting Markov chain!
    twitter.update_status(message)

    print('Sleeping for about thirty minutes...')
    # Bot will tweet once every 30 minutes or so while running
    time.sleep(60*25)

twitter = authenticate_twitter()

while True :
    run_bot(twitter)


