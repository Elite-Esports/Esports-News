import tweepy
from keys import bearer_token
import csv
import os


api = tweepy.Client(bearer_token) #use our specific bearer token to connect to our application on twitter dev account

def search_tweets(query, count):
    try:
        response = api.search_recent_tweets(query=search_query, max_results=count, tweet_fields = ["created_at", "public_metrics", "attachments"]) #searches for the query inputed, and asks for when the tweet was tweeted, public metrics, and attachments
        tweets = response.data  #the tweets themselves
        
        return tweets
    except Exception as e:
        print(f"unexpected error searching tweets: {e}")
        return None

def write_to_csv(file_name, tweets, query, column):
    try:
        with open(file_name, "a", newline='', encoding="utf-8") as file: #open file in append mode, use encoding for emoji's
            writer = csv.writer(file) #create the writer object
            #writer.writerow([column,"Date Created", "Likes", "Retweets" , "Replies", "Quotes", "Tweet"])  #column headers, separate the date and text
            for tweet in tweets: #for each tweet we will extract the wanted fields
                public_metrics = tweet.public_metrics
                created_at = tweet.created_at.strftime("%Y-%m-%d %H:%M:%S") if tweet.created_at else "N/A" #foramts the date, if no date was found returns N/A
                likes = public_metrics.get('like_count', 0)
                retweets = public_metrics.get('retweet_count', 0)
                replies = public_metrics.get('reply_count', 0)
                text = tweet.text.replace("\n", " ") if tweet.text else "No text available"
                quotes = public_metrics.get('quote_count', 0)   
                writer.writerow([query,created_at, likes, retweets, replies, quotes, text]) #writes the date and tweet
            print(f"tweets have been written to posts.csv !")
    except Exception as e: #error handling
            print(f"error while writing to csv file {e}")
#test cases
if __name__ == "__main__":
    usernames = ["FBRFeed"]
    keywords = [""]
    count = 10

    for username in usernames:
        if username:
            search_query = f"from:{username} -is:reply -is:retweet"  #search by username, filter out any replies or retweets
            tweets = search_tweets(search_query, count)
            query = f"#{username}"
            if tweets:
                query = username
                column = "Username"
                write_to_csv("posts.csv", tweets, query, column)
            else:
                print("error retrieving tweets")
        else:
            print("there is no username")
    
    for keyword in keywords:
        if keyword:
            search_query = f"{keyword} -is:reply -is:retweet"
            tweets = search_tweets(search_query, count)
            if tweets:
                query = keyword
                column = "Keyword"
                write_to_csv("posts.csv", tweets, query, column)
            else:
                print("error retrieving tweets")
        else:
            print("there is no keyword")
