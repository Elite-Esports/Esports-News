import tweepy #this allows us to work with twitter API using python

from keys import API_key, API_key_secret, bearer_token,access_token, access_token_secret 


authorization = tweepy.OAuthHandler(API_key, API_key_secret) #authorizes the use of the our app
authorization.set_access_token(access_token, access_token_secret)

#instance of the app
instance = tweepy.API(authorization, wait_on_rate_limit=True)

status = instance.verify_credentials() #built-in function in tweepy to check and see if we are authorized 

if status: 
  print('credientials are valid')
else:
  print('invalid')

  #this ran correctly and credentials are validd on 7/21/2024