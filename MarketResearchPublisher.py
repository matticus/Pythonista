# coding: utf-8

"""
Market Research Publisher
~~~~~~~~~~~~~~~~~~~~~~~~~
This project was created to streamline the process of distributing Market Research to multiple channels.  I regularly have URLs and commentary that need to be shared with:
	- Company internal Hipchat room
	- Community Slack channels
	- and my Twitter feed (@mhowell)
	
After trying to simplify this workflow on my phone with Launchpad Pro & x-callback-url, I found the process was still manual, requiring visits to multiple apps.
This project removes the apps from the equation and instead goes straight to each service's Web API.
Workflow Outline
~~~~~~~~~~~~~~~~
When run, this project:
	- Pulls the current clipboard contents (expecting a URL), and prompts the user to confirm it is the correct URL
	- Asks the user for commentary on the URL (if no commentary is provided, the Page Title of the URL is used)
	- The destination URL is then passed through bit.ly, creating a Short URL to report on visits
	- The combined post is then presented for preview.
	- Finally, prior to posting, the user is asked whether the post should go to internal Hipchat, or all channels
	- TODO: I am working on also writing the post to a history document in Dropbox, for reporting purposes.
Getting Started
~~~~~~~~~~~~~~~
All configuration is below in the "Configuration section".  You will need to setup / add your own credentials / tokens for each of the supported services.
"""
import urllib
import urllib2
import httplib
import clipboard
import console
import bs4
import twitter
import json
import webbrowser

##### Configuration #####

# bit.ly credentials
bitlytoken = "YOUR BITLY TOKEN"

# Twitter
# Uses Twitter account configured in iOS Preferences.

# Hipchat
hipchattoken = 'YOUR HIPCHAT TOKEN'
hipchatroom = 'YOUR HIPCHAT ROOM ID'
hipchatuser = 'YOUR HIPCHAT NAME'

# Slack
slacktoken = 'YOUR SLACK TOKEN'
slackchannel = '#YOUR SLACK CHANNEL' # Keep the "#"
slackuser = 'YOUR SLACK NAME'
slackemoji = ':tropical_drink:' # Any supported emoji or inage link
slackurl = 'YOUR SLACK WEBHOOK URL'

# TODO: Dropbox
dropboxkey = ''
dropboxfile = ''

##### End Configuration #####

# Set headers so sites don't think we're a bot.
hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Upgrade-Insecure-Requests': '1',
    'Accept-Encoding': 'none',
    'Connection': 'keep-alive'}

def shorten(url):
  api = 'https://api-ssl.bitly.com/v3/shorten'
  token = bitlytoken
  request = api + '?access_token=' + token + '&longURL=' + url

  usock = urllib2.urlopen(request)
  data = usock.read()
  dataJSON = json.loads(data)
  shortURL = dataJSON["data"]["url"]
  usock.close()
  return shortURL

def preptext():
  # Prepare content in clipboard

  # Get Clipboard
  clip = clipboard.get()
  
  print('\n(1) Preparing Text\n -Retrieved Clipboard: '+clip)
  	
  # Collect / validate desc and URL w/ user
  url = console.input_alert("URL?","",clip,"OK")
  
  desc = console.input_alert("Commentary?","","","OK")
  
  # Prepare URL
  if (len(url) < 1):
  	  ## Set the URL / title to empty
    finalurl, shorturl, title = ''
  	
  else:
    # Follow URL to final destination
    
    req = urllib2.Request(url,None,hdr)
    
    try: 
      res = urllib2.urlopen(req)
      finalurl = res.geturl()
    except urllib2.HTTPError, e:
      print 'HTTPError = ' + str(e.code)
    except urllib2.URLError, e:
      print 'URLError = ' + str(e.reason)
    except httplib.HTTPException, e:
      print 'HTTPException'
    except Exception:
      import traceback
      print 'Generic Exception: ' + traceback.format_exc()
      
    # Get title of URL page
    soupreq = urllib2.Request(finalurl,None,hdr)
    soup = bs4.BeautifulSoup(urllib2.urlopen(soupreq))
    title = soup.title.string

    # Convert to short URL via bit.ly
    shorturl = shorten(finalurl)
  
  # If description is empty, set it to URL title
  if (len(desc) < 1):
    desc = title
  
  # Put the combined message back on the
  # clipboard, as a fallback.
  clipboard.set(desc+' - '+shorturl)
  
  return finalurl, shorturl, title, desc

def post_twitter(desc, url):
  # Post description + url
  all_accounts = twitter.get_all_accounts()
  if len(all_accounts) >= 1:
    account = all_accounts[0]
    parameters = {'screen_name': account['username']}
    status, data = twitter.request(account, 'https://api.twitter.com/1.1/users/show.json', 'GET', parameters)
  
  # Trim description to tweetable size 
  # 140 Total - 22 bit.ly URL = 118
  
  shortdesc = (desc[:116] + '..') if len(desc) > 118 else data
  
  twitter.post_tweet(account, shortdesc +" "+ url)
  print('\n(2) Twitter Post Successful \n')

def post_slack_api(desc, url):
  # Post URL + Description to Slack
  
  msg = desc + ' <'+url+'>'
          
  values={"text": msg,
          "token" : slacktoken,
          "icon_emoji" : slackemoji,
          "channel" : slackchannel,
          "username" : slackuser }
  
  payload_json = json.dumps(values)
  data = urllib.urlencode({"payload": payload_json})
  req = urllib2.Request(slackurl, data)
  response = urllib2.urlopen(req)
  
  # Uncomment to validate testing.
  # ATM, Slack does not support deep URL schemes
  #webbrowser.open('slack://')
  
  print('\n(3) Slack Post Successful \n')

def post_hipchat_api(desc, url):
  # Post URL + Description
  
  msg = desc + ' <a href="'+url+'">' + url + '</a>'
  
  values = {'room_id' : hipchatroom,
          'from' : hipchatuser,
          'message' : msg,
          'color' : 'green',
          'auth_token' : hipchattoken }
  
  data = urllib.urlencode(values)
  
  posturl = 'https://api.hipchat.com/v1/rooms/message'
  
  req = urllib2.Request(posturl, data)
  response = urllib2.urlopen(req)
  
  # Uncomment to validate testing
  #webbrowser.open('hipchat://www.hipchat.com/room/'+hipchatroom)
  
  print('\n(4) Hipchat Post Successful \n')

def post_hipchat_app(desc, url):
  # Note: the 'message' attribute does not
  # appear to work as advertised. The message
  # does not prepopulate.
  #
  # You should be able to paste the proper 
  # message into the app from clipboard.
  webbrowser.open('hipchat://www.hipchat.com/room/'+hipchatroom+'?message=HelloWorld')
	
  print('\n(4) Hipchat Post Successful \n')

def dropbbox_write(desc,url,shorturl,title):
  # send date/time, title, Url, and text to dropbox
  print('\n(5) DropBox Write Successful \n')

def main():
  console.clear()
  
  print("---- Getting Started ----")
  
  # Collect / prepare text
  url, shorturl, title, desc = preptext()
  
  # Prompt with current content: post / edit / cancel
  preview = console.alert("Preview",desc+" - "+shorturl,"Post","Edit")
  
  if (preview == 2):
    ## Edit
    ### Prompt to edit remaining text (if any)
    desc = console.input_alert("Adjust Message","Edit to suit.",desc,"Post","OK")
  
  # Verify where to send messages
  target = console.alert("Where to?","Options:","All","Hipchat")
  
  # Distribute posts
  if (target == 1):
    post_twitter(desc,shorturl)
    post_slack_api(desc,shorturl)
    print "(6) Sending to all channels."
  else:
  	  print "(6) Sending just to Hipchat."
  
  # Use _api for direct posts and _app to load the local iOS app
  post_hipchat_api(desc,shorturl)
  #post_hipchat_app(desc,shorturl)
  #dropbox_write(desc,url,shorturl,title)

  # Display results in console
  print("\n---- All Finished! ----")

if __name__ == '__main__':
  main()
