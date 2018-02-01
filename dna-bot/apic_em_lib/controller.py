"""
This script calls "GET /network-device" API and print out
an easy to read list with device host name,device ip and device type
All simplify REST request functions and get authentication token function are in apicem.py
Controller ip, username and password are defined in apicem_config.py
"""
from  apicem import *


def getUser():
    # Controller ip, username and password are defined in apicem_config.py
    # The get() function is defined in apicem.py
    # Get token function is called in get() function
    output = ''
    try:
        resp= get(api="user")
        response_json = resp.json() # Get the json-encoded content from response
        print (json.dumps(response_json,indent=4),'\n') # Convert "response_json" object to a JSON formatted string and print it out
    except:
        print ("Something wrong with GET /user request")
        sys.exit()

    # Parsing raw response to list out all users and their role
    for item in response_json["response"]:
        output += "<h3>User \'%s\'</h3><br>role(s): "%(item["username"])
        for item1 in item["authorization"]:
            output += "%s, "%((item1["role"])[5:])
        output += "<br>"

    return output


def getDevList():
    device = []
    try:
        # The request and response of "GET /network-device" API
        resp = get(api="network-device")
        status = resp.status_code
        # Get the json-encoded content from response
        response_json = resp.json()
        # All network-device detail is in "response"
        device = response_json["response"]
        # Try un-comment the following line to see what we get

        # print(json.dumps(device,indent=4))
    except:
        print ("Something wrong, cannot get network device information")
        sys.exit()

    if status != 200:
        print (resp.text)
        sys.exit()

    if device == [] :   # Response is empty, no network-device is discovered.
        print ("No network device found !")
        sys.exit()

    device_list = []
    # Now extract host name, ip and type to a list. Also add a sequential number in front
    i=0
    for item in device:
        i+=1
        device_list.append([i,item["hostname"],item["managementIpAddress"],item["type"],item["serialNumber"],item["instanceUuid"]])

    return device_list

def getDevTable():
    device_list= getDevList()
    number_offset = 8
    hostname_offset = 29
    ip_offset = 13
    serialNo_offset = 13
    type_offset = 46



    output1 = """<pre><code class="language-none">
    ========  =============================  =============  =============  ==============================================\n
    number            hostname                    ip            Serial      type                                         \n
    ========  =============================  =============  =============  ==============================================\n"""



    for item1 in device_list:
        output1 = output1 + "%s %s" % (item1[0],' '*(number_offset+2-len(str(item1[0])))) #add number

        output1 = output1 + "%s %s" % (item1[1],' '*(hostname_offset+2-len(item1[1]))) #add hostname

        output1 = output1 + "%s %s" % (item1[2],' '*(ip_offset+2-len(item1[2]))) #add ip

        output1 = output1 + "%s %s" % (item1[3],' '*(serialNo_offset+2-len(item1[3]))) #add serial number

        output1 = output1 + "%s %s\n" % (item1[4],' '*(type_offset-len(item1[4]))) #add type


    output1 = output1 + """========  =============================  =============  =============  ==============================================\n</pre></code>"""


    return output1

def getDevConf(spark_input):
    device_list = getDevList()

    id = ""
    device_id_idx = 5

    user_input = spark_input
    user_input= user_input.lstrip() # Ignore leading space
    if int(user_input) in range(1,len(device_list)+1):
        id = device_list[int(user_input)-1][device_id_idx]
    else:
        print ("Oops! number is out of range, please try again or enter 'exit'")

    # Get IOS configuration API
    try:
        resp = get(api="network-device/"+id+"/config")
        status = resp.status_code
    except:
        print ("Something wrong with GET network-device/"+id+"/config !\n")
    try:
        response_json = resp.json()
        # Replace "\r\n" to "\n" to remove extra space line (Carriage Return)
        output = '<pre><code class="language-none">'
        output += response_json["response"].replace("\r\n","<br>")
        output += '</pre></code>'

        return output
    except:
        # For some reason IOS configuration is not returned
        if status == 204:
            print ("No Content in response of GET /network-device/id/config !")
        else:
            print ("Something wrong in response of GET /network-device/id/config!\n")
            print ("Response:\n",json.dumps(response_json,indent = 4))



def getIntList(spark_input):

    device_list = getDevList()

    user_input = spark_input
    user_input= user_input.lstrip()

    id = ""
    device_id_idx = 5
    if int(user_input) in range(1,len(device_list)+1): # Check if input is within range
        id = device_list[int(user_input)-1][device_id_idx]
    else:
        print ("Oops! number is out of range, please try again or enter 'exit'")


    # GET api request
    try:
        resp = get(api="interface/network-device/"+id)
        status = resp.status_code
    except:
        print ("Something wrong with GET %s\n"%s)
        sys.exit()

    try:
        response_json = resp.json()
        print ("Response:\n",json.dumps(response_json,indent = 4))
        output ='''
                <h1>%s</h1>
                <br>
                <p>Serial#: %s</p>
                <br>
                '''%(n["serialNo"],n["series"])
        for n in response_json["response"]:
            output +='''
                     <h3>Port %s</h3><br>
                     <h5>- MAC address: %s</h5><br>
                     <h5>- Status: %s</h5><br>
                     <h5>- Vlan: %s</h5><br>
                     <br>
                     '''%(n["portName"],n["macAddress"],n["status"],n["vlanId"])
        return output
    except:
        if status == 204:
            print ("No Content in response of GET %s"%selected_api)
        else:
            print ("Something wrong in response of GET %s!\n"%selected_api)
            print ("Response:\n",json.dumps(response_json,indent = 4))
