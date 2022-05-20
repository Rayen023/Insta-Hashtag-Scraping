import requests
import json
import sys
from pymongo import MongoClient

def getCreds() :
	""" Get creds required for use in the applications
	
	Returns:
		dictonary: credentials needed globally

	"""
	creds = dict() # dictionary to hold everything
	creds['access_token'] = 'EAAOMGzUr4jMBAJX3J3XjfMR3hOV4IdrUvekDW0Sg4AebZCzZA8HMCQdgvhZCB9nckm4hxQZBQyJBOlzZAZBZAG05cLkTBHZBmqZBBgScCIMriUScbiIMeXg1hAPKRpi8gpHnfpn9fPgZA6qawbNQZAUu5d4KIMvAacRZAs14tnXm8vGgAEXF88B5th80' # access token for use with all api calls
	creds['client_id'] = '998473414206003' # client id from facebook app IG Graph API Test
	creds['client_secret'] = 'f60f096f460911281ef3e0dd330cc6d1' # client secret from facebook app
	creds['graph_domain'] = 'https://graph.facebook.com/' # base domain for api calls
	creds['graph_version'] = 'v13.0' # version of the api we are hitting
	creds['endpoint_base'] = creds['graph_domain'] + creds['graph_version'] + '/' # base endpoint with domain and version
	creds['debug'] = 'no' # debug mode for api call
	creds['page_id'] = '110917468291105' # users page id
	creds['instagram_account_id'] = '17841401090138625' # users instagram account id
	creds['ig_username'] = 'rayen__ghali' # ig username
	return creds



def makeApiCall( url, endpointParams ) :
	""" Request data from endpoint with params
	
	Args:
		url: string of the url endpoint to make request from
		endpointParams: dictionary keyed by the names of the url parameters


	Returns:
		object: data from the endpoint

	"""

	data = requests.get( url, endpointParams ) # make get request

	response = dict() # hold response info
	response['url'] = url # url we are hitting
	response['endpoint_params'] = endpointParams #parameters for the endpoint
	response['endpoint_params_pretty'] = json.dumps( endpointParams, indent = 4 ) # pretty print for cli
	response['json_data'] = json.loads( data.content ) # response data from the api
	response['json_data_pretty'] = json.dumps( response['json_data'], indent = 4 ) # pretty print for cli
	return response # get and return content



def getHashtagInfo( params ) :
	""" Get info on a hashtag
	
	API Endpoint:
		https://graph.facebook.com/{graph-api-version}/ig_hashtag_search?user_id={user-id}&q={hashtag-name}&fields={fields}

	Returns:
		object: data from the endpoint

	"""

	endpointParams = dict() # parameter to send to the endpoint
	endpointParams['user_id'] = params['instagram_account_id'] # user id making request
	endpointParams['q'] = params['hashtag_name'] # hashtag name
	endpointParams['fields'] = 'id,name' # fields to get back
	endpointParams['access_token'] = params['access_token'] # access token

	url = params['endpoint_base'] + 'ig_hashtag_search' # endpoint url

	return makeApiCall( url, endpointParams ) # make the api call



def getHashtagMedia( params ) :
	""" Get posts for a hashtag
	
	API Endpoints:
		https://graph.facebook.com/{graph-api-version}/{ig-hashtag-id}/top_media?user_id={user-id}&fields={fields}
		https://graph.facebook.com/{graph-api-version}/{ig-hashtag-id}/recent_media?user_id={user-id}&fields={fields}

	Returns:
		object: data from the endpoint

	"""
	endpointParams = dict() # parameter to send to the endpoint
	endpointParams['user_id'] = params['instagram_account_id'] # user id making request
	endpointParams['fields'] = 'id,children,caption,comment_count,like_count,media_type,media_url,permalink' # fields to get back
	endpointParams['access_token'] = params['access_token'] # access token

	url = params['endpoint_base'] + params['hashtag_id'] + '/' + params['type'] # endpoint url

	return makeApiCall( url, endpointParams ) # make the api call

try : # try and get param from command line
	hashtag = sys.argv[1] # hashtag to get info on
except : # default to coding hashtag
	hashtag = 'JacquesChirac' # hashtag to get info on

params = getCreds() # params for api call
params['hashtag_name'] = hashtag # add on the hashtag we want to search for
hashtagInfoResponse = getHashtagInfo( params ) # hit the api for some data!
params['hashtag_id'] = hashtagInfoResponse['json_data']['data'][0]['id']; # store hashtag id

params['type'] = 'top_media' # set call to get top media for hashtag
hashtagTopMediaResponse = getHashtagMedia( params ) # hit the api for some data!


cluster = 'mongodb+srv://rayenghali:admin@cluster0.06cfs.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(cluster)

print(client.list_database_names())

db = client.test
print(db.list_collection_names())

posts = db.posts


for post in hashtagTopMediaResponse['json_data']['data'] : # loop over posts
	#result = posts.insert_one(post)
	print("\n\n---------- POST ----------\n") # post heading
	print("Link to post:") # label
	print(post['permalink']) # link to post
	print("\nPost caption:") # label
	print(post['caption']) # post caption

result = posts.insert_many(hashtagTopMediaResponse['json_data']['data'])