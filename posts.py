import tweepy
from keys import bearer_token
import csv
import os

api = tweepy.Client(bearer_token) #use our bearer token and connect to application on dev account

def search_tweets(query, count): #pass in username or keyword with how many tweets wanted
    try: 
        response = api.search_recent_tweets( #extract the necessary fields
            query=query,
            max_results=count,
            tweet_fields=["created_at", "public_metrics", "attachments", "author_id", "text"], 
            expansions=["author_id", "attachments.media_keys"],
            media_fields=["url"],
            user_fields=["username"]
        )
        #error handling
        if response.errors:
            raise Exception(response.errors)
        
        #extract tweet, user, and media information
        tweets = response.data #list of tweets
        users = {u["id"]: u for u in response.includes.get("users", [])} #map ids and media keys
        media = {m["media_key"]: m for m in response.includes.get("media", [])}

        if not tweets:
            raise Exception("No tweets found")

        tweets_with_urls = [] 
        for tweet in tweets:
            tweet_data = { #dictionary to store tweet details 
                "tweet": tweet,
                "attachments": [],
                "username": users.get(tweet.author_id, {}).get("username", "Unknown")
            } #check if tweet has attachments and then extract the urls to those attachments
            if "attachments" in tweet and "media_keys" in tweet.attachments:
                for key in tweet.attachments["media_keys"]:
                    if key in media:
                        url = media[key].get("url")
                        if url:
                            tweet_data["attachments"].append(url)
            tweets_with_urls.append(tweet_data) #add the tweet data last

        return tweets_with_urls
    except Exception as e:
        print(f"Error in search_tweets: {e}")
        return []

def write_to_csv(file_name, tweets_with_urls, keyword):
    try:
        #check if file exists
        file_exists = os.path.isfile(file_name)
        
        #open file in append mode, creating a new file if it does not exist
        with open(file_name, "a", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            
            #write the headers if file is new
            if not file_exists:
                writer.writerow(["Username", "Keywords", "Date Created", "Likes", "Retweets", "Replies", "Quotes", "Attachment URLs", "Tweet"])
            
            #write the data into csv file 
            for tweet_data in tweets_with_urls:
                tweet = tweet_data["tweet"]
                username = tweet_data["username"]
                public_metrics = tweet.public_metrics
                created_at = tweet.created_at.strftime("%Y-%m-%d %H:%M:%S") if tweet.created_at else "N/A"
                likes = public_metrics.get('like_count', 0)
                retweets = public_metrics.get('retweet_count', 0)
                replies = public_metrics.get('reply_count', 0)
                quotes = public_metrics.get('quote_count', 0)
                text = tweet.text.replace("\n", " ") if tweet.text else "No text available"
                attachments = ",".join(tweet_data["attachments"])
                writer.writerow([username, keyword, created_at, likes, retweets, replies, quotes, attachments, text])
            
            print(f"Tweets have been written to {file_name}!")
    #error handling
    except Exception as e:
        print(f"Error while writing to csv file: {e}")





#test cases
if __name__ == "__main__":
    usernames = ["FNCompReport"]  #list of usernames we want to extract from
    keywords = [""]  #list of keywords
    count = 10

    for username in usernames:
        if username:
            search_query = f"from:{username} -is:reply -is:retweet" #exclude replies and retweets
            tweets_with_urls = search_tweets(search_query, count)
            if tweets_with_urls: #if data is found we write to the csv fil
                write_to_csv("posts.csv", tweets_with_urls, " ")
            else:
                print(f"No tweets found or error retrieving tweets for {username}")

    for keyword in keywords:
        if keyword:
            search_query = f"{keyword} -is:reply -is:retweet"
            tweets_with_urls = search_tweets(search_query, count)
            if tweets_with_urls:
                write_to_csv("newposts.csv", tweets_with_urls, keyword)
            else:
                print(f"No tweets found or error retrieving tweets for keyword: {keyword}")
