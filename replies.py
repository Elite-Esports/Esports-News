
#this will grab posts and replies, most recent activity on an account, and write to tweets.txt
import tweepy  
import os  
import requests #
from keys import bearer_token  
import re #this will help us extract the small url if a tweet contains a reply
#import libs

#intialize the tweepy client using the bearer token given in dev portal
client = tweepy.Client(bearer_token)


def get_tweets(user_name, retrieve):
    try:
        #get the info associated with user name
        user = client.get_user(username=user_name).data
        if user is None:
            print(f"user {user_name} not found.")
            return None
        
        user_id = user.id #user id is specific to every account and is how we can retrieve tweets, likes, etc

        tweets_response = client.get_users_tweets(user_id, max_results=retrieve) #retreieve up to date tweets using id

        if tweets_response.data is None: #if no tweets were found
            print(f"no tweets found for user {user_name}.")
            return None

        tweets = tweets_response.data #the tweets themselves

        url_pattern = re.compile(r"https://t.co/\S+") #s+ is for an addition string  
        shortened_urls = [] #this is where we will store the shortened urls
        for tweet in tweets:
            urls = url_pattern.findall(tweet.text) #this will extract all urls in a tweet if there are any
            if urls:
                shortened_urls.append(urls)

        print("urls found: ", shortened_urls)
        print(f"retrieved tweets: {len(tweets)}") #number of tweets found

       
        return tweets
    #error handling
    except tweepy.TweepyException as e:
        print(f"tweepy error: {e}")
        return None

def expand_url(short_url):
    try:
        response = requests.head(short_url, allow_redirects=True)
        return response.url
    except requests.RequestException as e:
        print(f"Error expanding URL {short_url}: {e}")
        return None

def write_to_textfile(file_name, tweets):
    if tweets:
        try:
            #open file in append move, use encoding for emoji's
            with open(file_name, "a", encoding="utf-8") as file:
                for tweet in tweets:
                    if tweet.text: #if the tweet has text content
                        file.write(f"text: {tweet.text}\n") #write to the local storage 
                        print(f"text: {tweet.text}")
                    else:
                        print("tweet text empty")
        #error handling

        except Exception as e:
            print(f"unexpected error: {e}")


if __name__ == "__main__":

    #test cases
    user_name = input("Enter the username on X: ")

    
    retrieve = int(input("Enter the amount of tweets you want (5 <= x <= 100): "))

    if retrieve < 5 or retrieve > 100:
        print("Invalid input. Enter a number 5 - 100")
        quit() 

    
    tweets_gotten = get_tweets(user_name, retrieve)

    if tweets_gotten:
        write_to_textfile("tweets.txt", tweets_gotten)
        print("Finished processing tweets.")
