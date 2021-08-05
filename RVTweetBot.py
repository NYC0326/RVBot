import tweepy

def connect_api():
    # 트위터 Application에서 발급 받은 key 정보들 문자열로 입력
    bearer_token = "AAAAAAAAAAAAAAAAAAAAAIMjSQEAAAAA6gT%2B0g0rQaFyyvq8d9AxGWDUOJA%3Dc4oVoZQVto44d3keuDNayrYFvoQfFPBjM0wiEMDPuTdRW5o6wB"
    consumer_key = "J5B04Nh8JpE8FrdJntuuiCQGI"
    consumer_secret = "cxQg0D4RvCRLfrpu5DEDuEKxUzfBKKGX3B5T71OLs6t3Ri1jRU"
    access_token = "806164211986415617-NDuMDJjcTeTzva4dxaAq2tj056czdmL"
    access_token_secret = "lWgRvZ6VxVyNr4pSi0AE9WC7mEIZpTdsmUI12i0e4sZll"

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)

    return api

def get_tweets(api, username):
    tweets = api.user_timeline(username, tweet_mode='extended')

    return tweets

def UserTimelineCursor(api, screen_name):
    tweets = tweepy.Cursor(api.user_timeline, screen_name=screen_name, tweet_mode="extended").items(5)
    return tweets

api = connect_api()
RV_timeline = UserTimelineCursor(api, '@RVsmtown')
i = 1
'''
for RV_tweet in RV_timeline:
    print(f"{i}번째 트윗 : {RV_tweet.full_text}")
    i+=1
'''
pic = []
for RV_tweet in RV_timeline:
    print(RV_tweet.full_text, '\n----------------------\n')
    try:
        print(len(RV_tweet.extended_entities['media']))
        for count in range(0, len(RV_tweet.extended_entities['media'])):
            if RV_tweet.extended_entities['media'][count]['type']=="photo":
                pic.append(RV_tweet.extended_entities['media'][count]['media_url'])
                print(RV_tweet.extended_entities['media'][count]['media_url']   )
    except:
        print(" 사진이 없습니다 ")