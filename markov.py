# Markov Twitter Bot

# This bot will imitate a Twitter user. To do this, it will look at discussions around trending hashtags, create a
# Markov chain based on those discussions, then send out various (semi-coherent) tweets based on the Markov chain.

import tweepy
import time
import random
import langid
import language_check
from collections import Counter
from textblob import TextBlob
import re

# Four basic steps to the program
# 1) Read the source text
# 2) Build the Markov chain
# 3) Use the Markov Chain to generate a random phrase
# 4) Output the phrase

# To login to my bot's twitter account

# Since langid isn't always accurate, a list of foreign & english words it confuses is hard-coded
# It has to be this way because all the NLTK and other dictionary modules I found were only 32-bit, and I have 64-bit
# Python

invalid_words = ['que', 'la', 'de', 'o', '', 'esta', 'este', 'y', ',', '_', '=', '+', '*', '<', '>', '(', ')', '&',
                 '^', '%', '#', '?', '!', '.', 'las', 'los', 'da', 'acertar', 'e', 'com', 'es', 'porque', 'des', 'pero',
                 'sa']

valid_words = ['still', 'want', 'because', 'by putting different', 'mommies', 'milky', 'isn\'t', 'phenomenal', 'gotta',
               'headphones', 'then', 'prime', 'longer', 'your day better', 'felt', 'probably', 'an average to',
               'average', 'gig', 'tuned', 'obamacare', 'lightemup', 'transgender', 'don\'t', 'them even if', 'silk',
               'because we don\'t', 'models', 'than getting you', 'outside', 'me after eating', 'crises',
               'still being decisive', 'being', 'articuno', 'kitchen', 'i felt your', 'i cant stress', 'so nice to',
               'paris', 'spent', 'thrive', 'phone', 'toddler', 'rules', 'young', 'ghostwriter', 'after being spotted',
               'amazing', 'wanna', 'while you gain', 'seen', 'yesterday', 'wednesday wisdom']

class MyStreamListener(tweepy.StreamListener) :

    # override tweepy.StreamListener to add logic to on_status
    def on_status(self, status):

        # Emojis can't be encoded into .txt file, so only accept tweets without them
        try :
            print(status.text)
            file = open('tweets.txt', 'a')
            file.write(status.text + '\n')
        except UnicodeError :
            print('Tweet contained non UTF-8 chars; discarded.')
        except Exception :
            print('Tweet raised some other exception; discarded.')


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
    print('CONSTRUCTING CHAIN...!')
    words = text.split(' ')

    # Index should be 1, because the first word will be the key, and the subsequent word (at index 1) will be the value
    # You'll see what I mean...
    index = 1

    for word_value in words[index+1:] :

        # The first word is a key
        # To improve coherency, keys will be two words
        key = words[index-1] + ' ' + words[index]

        # If a word's key (the previous word) is already in the chain, add word_value to the value list
        if key in chain :
            chain[key].append(word_value)

        # if the key isn't already in the chain, create a value list
        else :
            chain[key] = [word_value]

        index += 1

    print(chain)
    return chain


# To generate the message
# Character limit of twitter is 140


def generate_message(chain, chosen_trend) :

    print('GENERATING MESSAGE!!')
    char_limit = 140 - (len(chosen_trend)+5)

    # To find the most common elements, a Counter object is used
    # turn the dict object returned by chain.key() into list with three word elements, turn that into a string split
    # by spaces, then turn back into list so Counter will work properly
    counter1 = Counter(' '.join(list(chain.keys())).split(' '))
    print(counter1.most_common(400))
    while True :
        # Generate the first word, and if it is valid the code will continue
        # The while loop ensures that the first word makes more sense and is one of the most common single words
        word1 = random.choice(counter1.most_common(400))[0]

        if is_english(word1) :
            print('Word: ' + str(word1))
            # create text blob for word1 to check part of speech
            try :
                print(word1 + '\'s part of speech: ' + TextBlob(word1).tags[0][1])
                p_o_s = TextBlob(word1).tags[0][1]
            except IndexError :
                print('Invalid character. Regenerating message!')
                return generate_message(chain, chosen_trend)

            if p_o_s != 'CC' and p_o_s != 'TO' and p_o_s != 'MD' and p_o_s != 'IN':
                break
            else :
                print('Unacceptable part of speech... Choosing different word!')

    print('First word: ' + word1)

    # After getting the first word, find a key that it belongs to and set word1 to that key
    for key in chain.keys() :
        if key.split(' ')[0] == word1:
            word1 = key
    print('First word followed by its two appropriate keys: ' + str(word1))

    # Check if all three words are English (only checked the first one before)
    if is_english(word1.lower()) :
        message = word1.capitalize()
    else :
        print('Regenerating message!')
        return generate_message(chain, chosen_trend)

    # while the length of message doesn't exceed 140 chars, keep adding words that follow the Markov chain
    while len(message) < char_limit :

        # add the previous two words before word1 in message if word1 doesn't already have three words
        if len(word1.split(' ')) < 2 :
            word1 = message.split(' ')[len(message.split(' '))-2] + ' ' + word1

        try :
            word2 = random.choice(chain[word1])
        except KeyError:
            print('\'' + word1 + '\' was not in the chain... regenerating message!')
            return generate_message(chain, chosen_trend)

        # if word1 has multiple occurrences of the same value (e.g. 'set': ['of', 'of', 'down', 'off', 'of']), then
        # select the value with the most occurrences ('of')
        for key, values in chain.items() :
            if key == word1 :
                print('Key: ' + key + '\nValue list: ' + str(values))

                # Find the mode
                counter2 = Counter(values)
                potential_word2 = counter2.most_common(1)[0][0]

                # prevent repeats
                if potential_word2 not in message :
                    word2 = str(potential_word2)
                    print('Most common word: ' + word2)
                # if the new word is a repeat or some other erroneous word, set the new word to the chosen trend or
                # just a different word
                elif '&amp' in potential_word2 or potential_word2 in message:

                    i = random.randint(0,5)
                    # 1 in 6 chance to choose the trend
                    if i % 5 == 0 :
                        word2 = chosen_trend
                    # 33% chance to choose some other random word
                    else :
                        word2 = random.choice(chain[word1])
                    print('\'' + potential_word2 + '\' was invalid; ' + word2 + ' has been chosen instead')
                # if the word is a repeat, just set it to a random value of the key
                else :
                    word2 = random.choice(chain[word1])
                    print('\'' + potential_word2 + '\' was a repeat; another random word has been chosen')

        print('Chosen word: ' + word2)

        # check if the words are English
        if is_english(word2.lower()):
            word1 = word2
            message += ' ' + word2
        # if is_english() keeps returning false because a non-English word only has one value,
        # restart the message
        else :
            print('Not English... Regenerating message!')
            return generate_message(chain, chosen_trend)
        # if the word ends with a period and the char count is past 100, end the tweet there.
        if ('.' in word2 or '?' in word2 or '!' in word2) and len(message) >= 100 :
            break

        print('Message: ' + message)

    # add the chosen trend to the end of the tweet if it's not already in there
    if chosen_trend not in message :
        message += ' ' + chosen_trend

    # Fix any grammatical errors if possible (Also occasionally fixes some foreign words)
    tool = language_check.LanguageTool('en-US')
    matches = tool.check(message)
    message = language_check.correct(message, matches)
    print('Grammarized message: ' + message)

    print('Message length: ' + str(len(message)))

    # If, for whatever reason, the final tweet exceeds twitter's char limit, generate a new message
    if len(message) > 140 :
        print('Length of message exceeded twitter\'s char limit... Regenerating!')
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

    if langid.classify(word)[0] == 'en' and word in invalid_words:
        print('Classified as English, but is foreign!')
        return False
    # langid has trouble classifying single foreign words, so this checks for the common ones
    elif langid.classify(word)[0] == 'en' or word in valid_words:
        print('English!')
        return True
    else:
        print('Not English!')
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

    # Go through a large amount of tweets from all users using a stream listener                      #
    #                                                                                                 #
    # ----------------------------------- STREAMING METHOD ------------------------------------------ #
    #                                                                                                 #
    # although there are several trending hashtags, the bot will choose one and use all of the tweets #
    # that include it                                                                                 #

    # get a random trending hashtag
    # check if they're in english by splitting them by capital letters
    chosen_trends = []
    for name in names :
        if is_english(' '.join(re.findall('[A-Z][^A-Z]*', name)).lower()) :
            chosen_trends.append(name)
    print(chosen_trends)
    i = random.randint(0, len(chosen_trends) - 1)
    chosen_trend = [chosen_trends[i]]
    print('\n***************\n\nThe bot will imitate tweets concerning ' + str(chosen_trend) + '\n\n***************\n')

    my_stream_listener = MyStreamListener()
    my_stream = tweepy.Stream(auth = twitter.auth, listener = my_stream_listener)

    # streams all tweets with trending hashtags send out by U.S. accounts
    my_stream.filter(track=chosen_trend, async=True, locations=[-169.90, 52.72, -130.53, 72.40,
                                                         -160.6, 18.7, -154.5, 22.3,
                                                         -124.90, 23.92, -66.37, 50.08])

    # However many seconds the program sleeps will determine how long the stream continues for
    # I use five minutes to get a TON of tweets, so I can build a good chain
    time.sleep(60*15)
    my_stream.disconnect()

    tweets = ''

    with open('tweets.txt', 'r') as file :
        tweets = file.read()

    # Generate the Markov chain
    chain = generate_chain(tweets)

    # Generate the message using the chain
    message = generate_message(chain, chosen_trend[0])

    print('The Markov chain: ' + message)

    # Tweet out the resulting Markov chain!
    twitter.update_status(message)

    print('Sleeping for about thirty minutes...')
    # Bot will tweet once every 30 minutes or so while running
    time.sleep(60*15)

twitter = authenticate_twitter()

while True :
    run_bot(twitter)
