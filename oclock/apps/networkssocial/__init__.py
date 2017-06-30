import tweepy
def twitter(request):
    consumer_key, consumer_secret, access_token, access_token_secret = "W3Z7YGtoureem0w4sWdQ2XgQB", "brv3Ca9JQSgFyL59FEBixYjUGoTPwSkezUR01sCSKFe9bZCRRR", "20201491-etHYN0196ZxLs3gD9pWVasmmfZN4Nbta7NsYs5Wcs", "tq9HmAztiUp5tSLIkK2HYo7qCPhDBg99Jg67sYZnvTikP"
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    api.update_status("Hola?")