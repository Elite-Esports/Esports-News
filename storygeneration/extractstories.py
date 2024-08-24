import tweepy  # Library to interact with Twitter API
from keys import bearer_token
import csv
import os
import json  # We will be writing to a JSON file

from keys import openai_api_key  # Import OpenAI API key
from keys import LANGCHAIN_API_KEY  # Import LangChain API key
from langchain_openai import ChatOpenAI  # Import the OpenAI class to communicate with API

# LangChain settings
LANGCHAIN_TRACING_V2 = True  # LangChain tracing flag
LANGCHAIN_ENDPOINT = "https://api.smith.langchain.com"  # API endpoint
LANGCHAIN_PROJECT = "AI news project"  # Project name

# Connect to Twitter API
api = tweepy.Client(bearer_token)  # Use our bearer token to connect to the application on the dev account

def search_tweets(query, count):
    """Search for tweets based on a query and return them with attachments and username."""
    try:
        response = api.search_recent_tweets(
            query=query,
            max_results=count,
            tweet_fields=["created_at", "public_metrics", "attachments", "author_id", "text"], 
            expansions=["author_id", "attachments.media_keys"],
            media_fields=["url"],
            user_fields=["username"]
        )
        
        if response.errors:
            raise Exception(response.errors)
        
        tweets = response.data or []
        users = {u["id"]: u for u in response.includes.get("users", [])}
        media = {m["media_key"]: m for m in response.includes.get("media", [])}
        
        if not tweets:
            raise Exception("No tweets found")
        
        tweets_with_urls = []
        for tweet in tweets:
            tweet_data = {
                "tweet": tweet,
                "attachments": [],
                "username": users.get(tweet.author_id, {}).get("username", "Unknown")
            }
            if "attachments" in tweet and "media_keys" in tweet.attachments:
                for key in tweet.attachments["media_keys"]:
                    if key in media:
                        url = media[key].get("url")
                        if url:
                            tweet_data["attachments"].append(url)
            tweets_with_urls.append(tweet_data)
        
        return tweets_with_urls
    except Exception as e:
        print(f"Error in search_tweets: {e}")
        return []

def write_to_csv(file_name, tweets_with_urls, keyword):
    """Write tweet data to a CSV file."""
    try:
        file_exists = os.path.isfile(file_name)
        
        with open(file_name, "a", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            
            if not file_exists:
                writer.writerow(["Username", "Keywords", "Date Created", "Likes", "Retweets", "Replies", "Quotes", "Attachment URLs", "Tweet"])
            
            for tweet_data in tweets_with_urls:
                tweet = tweet_data["tweet"]
                username = tweet_data["username"]
                public_metrics = tweet.public_metrics or {}
                created_at = tweet.created_at.strftime("%Y-%m-%d %H:%M:%S") if tweet.created_at else "N/A"
                likes = public_metrics.get('like_count', 0)
                retweets = public_metrics.get('retweet_count', 0)
                replies = public_metrics.get('reply_count', 0)
                quotes = public_metrics.get('quote_count', 0)
                text = tweet.text.replace("\n", " ") if tweet.text else "No text available"
                attachments = ",".join(tweet_data["attachments"])
                writer.writerow([username, keyword, created_at, likes, retweets, replies, quotes, attachments, text])
            
            print(f"Tweets have been written to {file_name}!")
    except Exception as e:
        print(f"Error while writing to CSV file: {e}")

def process_tweets(tweets_file, starting_row, ending_row):
    """Process tweets from a CSV file and format them as JSON."""
    tweets_data = []
    try:
        with open(tweets_file, "r", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            for number, row in enumerate(reader):
                if starting_row <= number < ending_row:
                    username, keywords, date_created, likes, retweets, replies, quotes, media, tweet_text = row
                    tweet = {
                        'username': username,
                        'media': media if media else 'N/A',
                        'tweet': tweet_text
                    }
                    tweets_data.append(tweet)
        formatted_tweets = json.dumps(tweets_data, indent=2, ensure_ascii=False)
        return formatted_tweets
    except Exception as e:
        print(f"Error in process_tweets: {e}")
        return json.dumps([])  # Return an empty JSON array in case of error

def generate_stories(formatted_tweets, prompt, stories_file):
    """Generate news stories from formatted tweets using LangChain and save them to a JSON file."""
    try:
        llm = ChatOpenAI(temperature=0.5, model_name="gpt-4o-mini", openai_api_key=openai_api_key)
        
        full_prompt = prompt + "\n\n" + formatted_tweets
        response = llm.invoke(full_prompt)
        
        isolated = response.content
        print(isolated)
        with open(stories_file, 'a', encoding='utf-8') as f:
            f.write(isolated)
        return isolated
    except Exception as e:
        print(f"Error in generate_stories: {e}")

def clearstoriesfile(file): #we will erase the json file before we start adding a group of stories 
    with open(file, 'w') as file:
        json.dump('', file)

# Test cases
if __name__ == "__main__":

    clearstoriesfile("stories.json")
    count = 10  # Adjust this value to control how many tweets per story
    starting_row = 650

    prompt = """  
    Task:
    Your task is to generate as many engaging and specific news articles as you can using the information provided in the tweets passed in with this prompt. Your goal is to identify key topics and themes within these tweets and craft articles that provide in-depth insights and exciting narratives based on the information and being as specific as possible. The article should be no longer than 100 words, so separate the information accordingly.

    Topic Examples for Stories:
    Fortnite updates, competitive play, game gossip, player achievements, statistical analysis

    Input:
    The input data is provided in a JSON format with the following fields: username, link to an image (if available), and the tweet itself. These tweets are ordered from greatest to least liked. Carefully analyze the tweets to extract meaningful and relevant information, focusing on trends, achievements, and notable events within the Fortnite community.

    Audience:
    The Fortnite community and competitive esports followers who are interested in reading engaging, suspenseful, and attention-grabbing stories in a short form. Your stories should resonate with this audience by connecting individual tweets to broader trends or emerging narratives within the game.

    Exclude:
    Do not mention the username in the stories themselves.
    - Ignore any tweets or parts of tweets that focus on user self-promotion, follower counts, or other irrelevant details unrelated to gossip, competitive play, or game updates.
    - Disregard any giveaway shoutouts
    -These articles should solely be about the topics discussed, not about the accounts from the tweets. 

    Output:
    Your job is to output these news articles in an isolated JSON format:
    - headline: The headline generated related to the article (include how much time it will take to read the article)
    - article: A detailed and engaging article using specific tweets with the same topic. Ensure the article captures the context, relevance, and impact of the information presented in the tweets.
    - media: If any tweet used for an article contains a link in the 'media' field, include it in this field
    - usernames: the usernames that belong to the media field
    - topic: topic of the article (example: gossip, update, competitive)

    Examples:
    the following are example articles, the information in these articles should not be used in the articles you generate, but the overall tone should be the same:
    Topic: Update
    Headline: Game Updates and Patches
    Article: Marvel is making a grand re-entry into the Fortnite universe. The Iron-Spider skin is set to be released on August 24th, and the Marvel x Fortnite LTMs are making a comeback. Players can choose between 'Heroes' and 'Villains,' adding a fresh layer of strategy and excitement to the game. This season will feature two Marvel LTMs, both bringing back OG Fortnite x Marvel Mythics, promising a nostalgic yet thrilling experience for fans.
    Attachments:
    https://pbs.twimg.com/media/GVMqsW1XYAA4_rV.jpg https://pbs.twimg.com/media/GVMx2ykXEAEpzo8.jpg 


    Topic Fortnite Competitive
    Headline: 
    Epic Fortunes and Close Calls: Fortnite's Solo Cash Cup Heats Up (30 s read)

    Article: The C5S3 Solo Cash Cup saw intense competition, with standout performances from players across the globe. 🇨🇿 @F1shyX_ led Round 1 with 43 eliminations, closely followed by 🇫🇷 @SeyytoFN and 🇧🇷 @LetzFN. In the finals, 🇧🇭 @Pumafv secured the most wins with 37 eliminations, while 🇦🇹 @Vicotryona and 🇧🇷 @teuzzfn followed closely. Notably, 🇺🇸 @coldfv and 🇺🇸 @PeterbotFN nearly broke the 40+ elimination mark but fell just short. The competition was fierce, with 382 players reaching the finals without a win, proving how tough it is at the top. Fortnite’s competitive scene continues to thrill fans worldwide.


    Include:
    Try to include all information from tweets into these stories if the information is informative.
    Try to use less filler words and make it sound as human, engaging, and informative as possible
    """
    usernames = ["yoxics"]

    for username in usernames:
        if username:
            search_query = f"from:{username} -is:reply -is:retweet"  # Exclude replies and retweets
            tweets_with_urls = search_tweets(search_query, count)
            if tweets_with_urls:
                write_to_csv("posts.csv", tweets_with_urls, " ")
                ending_row = starting_row + len(tweets_with_urls)
                formatted_tweets = process_tweets("posts.csv", starting_row-1, ending_row)
                print(formatted_tweets)
                stories = generate_stories(formatted_tweets, prompt, "stories.json")
                starting_row = ending_row

            else:
                print(f"No tweets found or error retrieving tweets for {username}")
    keywords = [""]
    for keyword in keywords:
        if keyword:
            search_query = f"{keyword} -is:reply -is:retweet"
            tweets_with_urls = search_tweets(search_query, count)
            if tweets_with_urls:
                write_to_csv("newposts.csv", tweets_with_urls, keyword)
                ending_row = starting_row + len(tweets_with_urls)
                formatted_tweets = process_tweets("newposts.csv", starting_row-1, ending_row)
                print(formatted_tweets)
                stories = generate_stories(formatted_tweets, prompt, "stories.json")
            else:
                print(f"No tweets found or error retrieving tweets for keyword: {keyword}")
