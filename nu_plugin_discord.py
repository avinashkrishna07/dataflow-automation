#!/usr/bin/env python3

import os
import sys
import json
import re

try:
    import selenium
except:
    os.system("pip install -U selenium")

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys

def tell_nushell_encoding():
    sys.stdout.write(chr(4))
    for ch in "json":
        sys.stdout.write(chr(ord(ch)))
    sys.stdout.flush()

def signatures():
    """
    Signatures for the gmail command
    """
    return '''
{
  "Signature": [
    {
      "sig": {
        "name": "discord",
        "usage": "Perform operations on discord",
        "extra_usage": "",
        "search_terms": [],
        "required_positional": [],
        "optional_positional": [],
        "rest_positional": null,
        "vectorizes_over_list": false,
        "named": [
          {
            "long": "help",
            "short": "h",
            "arg": null,
            "required": false,
            "desc": "Display the help message for this command",
            "var_id": null,
            "default_value": null
          }
        ],
        "input_type": "Any",
        "output_type": "Any",
        "input_output_types": [],
        "allow_variants_without_examples": false,
        "is_filter": false,
        "creates_scope": false,
        "allows_unknown_args": false,
        "category": "Filters"
      },
      "examples": []
    },
    {
      "sig": {
        "name": "discord list",
        "usage": "List all user list",
        "extra_usage": "",
        "search_terms": [],
        "required_positional": [],
        "optional_positional": [],
        "rest_positional": null,
        "vectorizes_over_list": false,
        "named": [
          {
            "long": "help",
            "short": "h",
            "arg": null,
            "required": false,
            "desc": "Display the help message for this command",
            "var_id": null,
            "default_value": null
          }
        ],
        "input_type": "Any",
        "output_type": "Any",
        "input_output_types": [],
        "allow_variants_without_examples": false,
        "is_filter": false,
        "creates_scope": false,
        "allows_unknown_args": false,
        "category": "Network"
      },
      "examples": []
    },
    {
      "sig": {
        "name": "discord send",
        "usage": "Send messsage to one or more discord ids",
        "extra_usage": "",
        "search_terms": [],
        "required_positional": [
          {
            "name": "msg",
            "desc": "The message to be sent",
            "shape": "String",
            "var_id": null,
            "default_value": null
          }
        ],
        "optional_positional": [],
        "rest_positional": null,
        "vectorizes_over_list": false,
        "named": [
          {
            "long": "help",
            "short": "h",
            "arg": null,
            "required": false,
            "desc": "Display the help message for this command",
            "var_id": null,
            "default_value": null
          }
        ],
        "input_type": "Any",
        "output_type": "Any",
        "input_output_types": [],
        "allow_variants_without_examples": false,
        "is_filter": false,
        "creates_scope": false,
        "allows_unknown_args": false,
        "category": "Network"
      },
      "examples": []
    }
  ]
}
    '''


def getBrowser():
    option = webdriver.ChromeOptions()
    option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    browser = webdriver.Chrome(options=option)
    main_window = browser.window_handles[0]

    browser.maximize_window()

    return browser

def listReceivers(plugin_call,browser):
    list_path = """//a[contains(@aria-label,"direct message")]"""
    elements = browser.find_elements(By.XPATH,list_path)
    ids = []
    names = []
    for ele in elements:
        id = re.findall('https://discord.com/channels/@me/(.*)',ele.get_attribute('href'))
        if id != []:
            name = ele.get_attribute('aria-label').replace(" (direct message)",'').strip()
            ids.append(id[0])
            names.append(name)

    ret = {
        "Value": {
            "List": {
                "vals": [
                    {
                        "Record": {
                            "cols": [
                                "id",
                                "name",
                            ],
                            "vals": [
                                {
                                    "String": {
                                        "val": ids[i],
                                        "span": plugin_call["CallInfo"]["call"]["head"]
                                    }
                                },
                                {
                                    "String": {
                                        "val": names[i],
                                        "span": plugin_call["CallInfo"]["call"]["head"]
                                    }
                                },
                                ],
                            "span": plugin_call["CallInfo"]["call"]["head"]
                        }
                    }
                    for i in range(len(names))],
                "span": plugin_call["CallInfo"]["call"]["head"]
            }
        }
    }
    return ret


def extract_id(plugin_call):
    # Take: id, [id], row, [row]

    def extract(single):
        if 'Record' in single:
            idx = single["Record"]["cols"].index("id")
            return single["Record"]["vals"][idx]["String"]["val"]
        elif 'String' in single:
            return single["String"]["val"]
        else:
            return None


    ip = plugin_call["CallInfo"]["input"]
    if 'Value' not in ip:
        return {
            "Error": {
                "label": "No input given",
                "msg": "STDIN was empty",
                "span": {"start": 0, "end": 1},
            }
        }

    links = []
    if 'List' in ip['Value']:
        for val in ip["Value"]["List"]["vals"]:
            ext = extract(val)
            if ext is not None:
                links.append(ext)
    else:
        ext = extract(ip["Value"])
        if ext is not None:
            links.append(ext)

    return links

def handle_error(err):
    error = {
        "Error": {
            "label": "ERROR from plugin",
            "msg": str(err),
            "span": {"start": 0, "end": 1},
        }
    }
    return error

def handle_suc(plugin_call):
    suc = {
        "Value": {
            "Nothing": {
                "span": plugin_call["CallInfo"]["call"]["head"]
            }
        }
    }
    return suc

def sendMessage(plugin_call,browser):
    ids = extract_id(plugin_call)

    try:
        for d_id in ids:
            receiver = f"""//a[@href="/channels/@me/{d_id}"]"""
            receiver_sidebar_avatar = browser.find_element(By.XPATH,receiver)
            receiver_sidebar_avatar.click()

            message_box = '//div[@role="textbox"]'
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, message_box)))
            message_prompt = browser.find_element(By.XPATH,message_box)

            msg = plugin_call["CallInfo"]["call"]["positional"][0]["String"]["val"]
            message_prompt.send_keys(msg)
            message_prompt.send_keys(Keys.ENTER)

        suc = {
            "Value": {
                "Nothing": {
                    "span": plugin_call["CallInfo"]["call"]["head"]
                }
            }
        }
        return suc
    except Exception as E:
        return handle_error(E)


def startDiscord(plugin_call):
    browser = getBrowser()
    browser.get("https://discord.com/login")

    # Wait for heading to appear (discord loaded!)
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//nav[@aria-label="Servers sidebar"]')))

    if plugin_call["CallInfo"]["name"] == "discord list":
        return listReceivers(plugin_call,browser)
    elif plugin_call["CallInfo"]["name"] == "discord send":
        return sendMessage(plugin_call,browser)



# Make the discord plugin work properly with nushell not sure about the CallInfo structure
def plugin():
    tell_nushell_encoding()

    call_str = ",".join(sys.stdin.readlines())
    plugin_call = json.loads(call_str)

    if plugin_call == "Signature":
        signature = signatures()
        sys.stdout.write(signature)
    elif "CallInfo" in plugin_call:
        print(plugin_call, file=sys.stderr)

        response = startDiscord(plugin_call)
        sys.stdout.write(json.dumps(response))
    else:
        error = {
            "Error": {
                "label": "ERROR from plugin",
                "msg": "error message pointing to call head span",
                "span": {"start": 0, "end": 1},
            }
        }
        sys.stdout.write(json.dumps(error))


if __name__ == '__main__':
    plugin()

    # startDiscord({
    #     "CallInfo": {
    #         "name": "discord list",
    #         "receiver_id" : "921697222096220162",
    #         "msg": "Troll"
    #     }
    # })
