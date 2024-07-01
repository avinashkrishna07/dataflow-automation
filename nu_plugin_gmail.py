#!/usr/bin/env python3

import re
import os
import sys
import json
from datetime import datetime

try:
    import selenium
except:
    os.system("pip install -U selenium")

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys

from persistent_cache import PersistentCache


GMAIL_HOMEPAGE = "https://mail.google.com/mail/u/{}"
GMAIL_STATIC_HOMEPAGE = GMAIL_HOMEPAGE + "/h/1pq68r75kzvdr/?v%3Dlui"
cache = PersistentCache('gmail.pkl')


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
        "name": "gmail",
        "usage": "Perform operations on gmail",
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
        "name": "gmail list",
        "usage": "List all emails",
        "extra_usage": "",
        "search_terms": [],
        "required_positional": [],
        "optional_positional": [
          {
            "name": "user_id",
            "desc": "User identifier (n'th account logged into browser)",
            "shape": "Int",
            "var_id": null,
            "default_value": null
          }
        ],
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
          },
          {
            "long": "force-reload",
            "short": "f",
            "arg": null,
            "required": false,
            "desc": "Force invalidate cache",
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
        "name": "gmail open",
        "usage": "Open set of email(s)",
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
        "name": "gmail archive",
        "usage": "Archive set of email(s)",
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
        "name": "gmail delete",
        "usage": "Delete set of email(s)",
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
    }
  ]
}
    '''


def gmail_list(plugin_call, browser):
    user_id = 0
    if len(plugin_call["CallInfo"]["call"]["positional"]) > 0:
        user_id = plugin_call["CallInfo"]["call"]["positional"][0]["Int"]["val"]

    if not (len(plugin_call["CallInfo"]["call"]["named"]) > 0 and len(plugin_call["CallInfo"]["call"]["named"][0]) > 0 and plugin_call["CallInfo"]["call"]["named"][0][0]["item"] == 'force-reload'):
        cached = cache.get(user_id)
        if cached is not None:
            return cached


    browser.get(GMAIL_STATIC_HOMEPAGE.format(user_id))

    email_container = browser.find_element(By.XPATH, '//table[@class="th"]')
    emails = email_container.find_elements(By.XPATH, './/tr')

    links = []
    for email in emails:
        permalink = email.find_element(
            By.XPATH, './/td[3]/a').get_attribute('href')
        links.append(permalink)

    browser.get(GMAIL_HOMEPAGE.format(user_id))

    # Wait for heading to appear (gmail loaded!)
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[@class="gb_He"]')))
    email_container = browser.find_element(By.XPATH, '//div[@class="Cp"]')
    emails = email_container.find_elements(By.XPATH, './/tr')

    names = []
    froms = []
    subjects = []
    dates = []
    for i, email in enumerate(emails):
        metadata = email.find_element(By.XPATH, './/td[4]/div/span/span')

        name = metadata.get_attribute('innerHTML')
        frm = metadata.get_attribute('email')
        subject = email.find_element(
            By.XPATH, './/td[4]/div/span[2]').get_attribute('innerHTML')
        date = email.find_element(
            By.XPATH, './/td[8]/span').get_attribute('title')

        subject = subject.replace('\n', ' ')
        # serialize emoji
        subject = re.sub(r'<img.*?alt="([^"]+).*?>', r'\1', subject)

        names.append(name)
        froms.append(frm)
        subjects.append(subject)
        dates.append(date)

    # print('\n'.join(results))
    ret = {
        "Value": {
            "List": {
                "vals": [
                    {
                        "Record": {
                            "cols": [
                                "name",
                                "from",
                                "subject",
                                "date",
                                "permalink"
                            ],
                            "vals": [
                                {
                                    "String": {
                                        "val": names[i],
                                        "span": plugin_call["CallInfo"]["call"]["head"]
                                    }
                                },
                                {
                                    "String": {
                                        "val": froms[i],
                                        "span": plugin_call["CallInfo"]["call"]["head"]
                                    }
                                },
                                {
                                    "String": {
                                        "val": subjects[i],
                                        "span": plugin_call["CallInfo"]["call"]["head"]
                                    }
                                },
                                {
                                    "Date": {
                                        "val": datetime.strptime(dates[i], "%a, %b %d, %Y, %I:%M %p").strftime("%Y-%m-%dT%H:%M:%S.%f%z+05:30"),
                                        "span": plugin_call["CallInfo"]["call"]["head"]
                                    }
                                },
                                {
                                    "String": {
                                        "val": links[i],
                                        "span": plugin_call["CallInfo"]["call"]["head"]
                                    }
                                },
                                ],
                            "span": plugin_call["CallInfo"]["call"]["head"]
                        }
                    }
                    for i in range(len(links))],
                "span": plugin_call["CallInfo"]["call"]["head"]
            }
        }
    }
    cache.set(user_id, ret)
    return ret

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

def gmail_open(plugin_call, browser, mail_ids):
    try:
        for mail_id in mail_ids:
            body = browser.find_element(By.TAG_NAME,"body")
            browser.execute_script(f"window.open('{mail_id}','_blank');", body);
        return handle_suc(plugin_call)
    except Exception as E:
        return handle_error(E)

def gmail_delete(plugin_call, browser, mail_ids):
    try:
        for mail_id in mail_ids:
            browser.get(mail_id)
            emailDeleteButton = browser.find_elements(By.XPATH, '//input[@name="nvp_a_tr"]')
            emailDeleteButton[0].click()
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@id="guser"]')))
        return handle_suc(plugin_call)
    except Exception as E:
        return handle_error(E)

def gmail_archive(plugin_call, browser, mail_ids):
    try:
        for mail_id in mail_ids:
            browser.get(mail_id)
            emailArchieveButton = browser.find_elements(By.XPATH, '//input[@name="nvp_a_arch"]')
            emailArchieveButton[0].click()
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@id="guser"]')))
        return handle_suc(plugin_call)
    except Exception as E:
        return handle_error(E)

def extract_links(plugin_call):
    # Take: id, [id], row, [row]

    def extract(single):
        if 'Record' in single:
            idx = single["Record"]["cols"].index("permalink")
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

def gmail(plugin_call):
    option = webdriver.ChromeOptions()
    option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    browser = webdriver.Chrome(options=option)
    main_window = browser.window_handles[0]

    browser.maximize_window()
    links_list = extract_links(plugin_call)
    if plugin_call["CallInfo"]["name"] == "gmail list":
        return gmail_list(plugin_call, browser)
    elif plugin_call["CallInfo"]["name"] == "gmail open":
        return gmail_open(plugin_call,browser,links_list)
    elif plugin_call["CallInfo"]["name"] == "gmail delete":
        return gmail_delete(plugin,browser,links_list)
    elif plugin_call["CallInfo"]["name"] == "gmail archive":
        return gmail_archive(plugin_call,browser,links_list)
    # elif plugin_call["CallInfo"]["name"] == "gmail forward":
    #     return gmail_list(plugin_call, browser)

    return {
        "Error": {
            "label": "ERROR from plugin",
            "msg": json.dumps(plugin_call),
            "span": {"start": 0, "end": 1},
        }
    }


def plugin():
    tell_nushell_encoding()

    call_str = ",".join(sys.stdin.readlines())
    plugin_call = json.loads(call_str)

    if plugin_call == "Signature":
        signature = signatures()
        sys.stdout.write(signature)
    elif "CallInfo" in plugin_call:
        print(plugin_call, file=sys.stderr)
        response = gmail(plugin_call)
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
