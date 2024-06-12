from .shared import dict_report, target
from .statuses import http_status_codes
from .args import argparser

args = argparser()
target_url = args.url
if (target_url[len(target_url) - 1] == '/'):
    target_url = target_url[:len(target_url)-1]

def clean_urls(url):
    if(url[:4] == "http"):    
        return url
    elif (url[0] != "/"):
        url = target_url + "/" + url
        return url
    else:
        url = target_url + url
    return url
  
def parse_domain(http_url):
    url_pieces = http_url.split("/", 3)
    domain_labels = url_pieces[2].split(".")
    registered_domain = domain_labels[-2] + "." + domain_labels[-1] 
    return registered_domain

def remove_dupes(all_dirs):
    all_dirs[:] = list(dict.fromkeys(all_dirs))

def create_report(url, request, status_code, final_location, **headers):
    dict_report[url]['requests'][request]['code'] = status_code
    dict_report[url]['requests'][request]['message'] = http_status_codes.get(status_code, False)
    dict_report[url]['final_location'] = str(final_location)
    http_dict = headers["headers"]
    http_keys = []
    http_values = []

    for key in http_dict.keys():
        http_keys.append(key)

    for value in http_dict.values():
        http_values.append(value)

    header_dict = dict(zip(http_keys, http_values))
    dict_report[url]['headers'] = header_dict
