from itty import *
import urllib2
import json
from apic_em_lib import *

def sendSparkGET(url):
    """
    This method is used for:
        -retrieving message text, when the webhook is triggered with a message
        -Getting the username of the person who posted the message if a command is recognized
    """
    request = urllib2.Request(url,
                            headers={"Accept" : "application/json",
                                     "Content-Type":"application/json"})
    request.add_header("Authorization", "Bearer "+bearer)
    contents = urllib2.urlopen(request).read()
    return contents

def sendSparkPOST(url, data):
    """
    This method is used for:
        -posting a message to the Spark room to confirm that a command was received and processed
    """
    request = urllib2.Request(url, json.dumps(data),
                            headers={"Accept" : "application/json",
                                     "Content-Type":"application/json"})
    request.add_header("Authorization", "Bearer "+bearer)
    contents = urllib2.urlopen(request).read()
    return contents


@post('/')
def index(request):
    """
    When messages come in from the webhook, they are processed here.  The message text needs to be retrieved from Spark,
    using the sendSparkGet() function.  The message text is parsed.  If an expected command is found in the message,
    further actions are taken. i.e.
    /batman    - replies to the room with text
    /batcave   - echoes the incoming text to the room
    /batsignal - replies to the room with an image
    """
    webhook = json.loads(request.body)
    print webhook['data']['id']
    result = sendSparkGET('https://api.ciscospark.com/v1/messages/{0}'.format(webhook['data']['id']))
    result = json.loads(result)
    msg = None
    if webhook['data']['personEmail'] != bot_email:
        in_message = result.get('text', '').lower()
        in_message = in_message.replace(bot_name, '')
	device_list= controller.getDevList()
        if 'get users' in in_message:
            msg = controller.getUser()
        elif 'device list' in in_message:
            msg = controller.getDevTable()
        elif 'device config' in in_message:
            in_message = in_message.replace('device config', '')
	    in_message = in_message.replace(' ','')    
	    if in_message == '':
		msg = "Please specify device number."
            elif int(in_message) in range(1,len(device_list)+1):
                msg = controller.getDevConf(in_message)
            else:
                msg = "invalid number, please choose a number from the list, use the `device list` command to display the list"
        elif 'device interfaces' in in_message:
            in_message = in_message.replace('device interfaces', '')
            in_message = in_message.replace(' ','') 
            if in_message == '':
                msg = "Please specify device number."
            elif int(in_message) in range(1,len(device_list)+1):
                msg = controller.getIntList(in_message)
		msg = msg.split('<split>',1)
            else:
                msg = "invalid number, please choose a number from the list, use the `device list` command to display the list"
        else:
            msg = "\
            Command List: <br>\
            - **get users** <br>\
            - **device list** <br>\
            - **device config** (device number from list) <br>\
            - **device interfaces** (device number from list) "


        #send message to room
        if msg != None:
            print msg
	    if isinstance(msg, list):
	    	for message in msg:
			message = "%s"%message
			sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "markdown": message})
            else:
		sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "markdown": msg})

    return "true"

####CHANGE THESE VALUES#####
bot_email = "ozgebot@sparkbot.io"
bot_name = "DNA Manager Bot"
bearer = "ZGQ5ZTA0MGEtNGUwZS00ZWYzLTk1MWUtOTY2M2Y1ZmU4ODdhMTJkYTY4MjEtYzEz"
#bat_signal  = "https://upload.wikimedia.org/wikipedia/en/c/c6/Bat-signal_1989_film.jpg"
run_itty(server='wsgiref', host='0.0.0.0', port=10010)
