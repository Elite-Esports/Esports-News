# Esports-News

# Authorize.py:
this script is to test if the tokens and our developer keys are authorized to start using Twitter-API by using the library Tweepy. Tweepy allows us to interact with Twitter Api using python. To download: pip install Tweepy. Access the necessary tokens from twitter dev account/. 


# Posts.py:
this script lets us search and retrieve tweets by keyword and username. Per request, each account can retrieve up to 100 tweets, and each keyword/keywords can retrieve up to 100. The search_tweets function takes in a search query (either username or keyword), a maximum count for the number of tweets wanted, and then retrieves recent tweets. We then call the write_to_csv function to write the retrieved posts to the organized csv file, separating the tweet and the time it was created. 

example:
For usernames, it searches for tweets posted by the user, excluding replies and retweets. For keywords, it searches for tweets containing the keyword or keywords depending on the string, again excluding replies and retweets. In both cases, it retrieves a total of 10 tweets and writes them to posts.csv

# replies.py:
This is the initial script and takes in an input from the terminal. It takes in a username, count, will return the most recent activity on that account, and store in tweets.txt. However, this script does not exclude replies, and will return the link to the replied tweet if given in the tweet. 
