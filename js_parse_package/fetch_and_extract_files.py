import requests, re, jsbeautifier
from bs4 import BeautifulSoup
from .args import argparser
from .show_results import pretty_files

args = argparser()

def extract_files(url):
    for tags in fetch_html(url):
        try: 
            js_file = tags['src']
            yield js_file
        except KeyError:
            pass

def fetch_html(url):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'}
    req=""

    try:
        req = requests.get(url, headers=headers)
        soup = BeautifulSoup(req.content, "html.parser")
        list_tags = soup.find_all('script')
        return list_tags
    except ( requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema, requests.exceptions.InvalidURL):
            print(f'NOT FOUND: invalid url, missing, or does not start with http:// or https:// in {url}')
            quit()
   

def extract_urls(url):
    req = fetch_js(url)
    absolute_pattern = r'(["\'])(https?://(?:www\.)?\S+?)\1'
    relative_dirs = re.findall('["\'][\w\.\?\-\_]*/[\w/\_\-\s\?\.=]*["\']*', req)
    absolute_urls = re.findall(absolute_pattern, req)
    absolute_urls = [url[1] for url in absolute_urls] 
    all_dirs = relative_dirs + absolute_urls
    return all_dirs

def fetch_js(url):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'}
    req = requests.get(url, headers=headers).text
    req = jsbeautifier.beautify(req)
    if(args.save):
        pretty_files.append(url)
        with open(f"pretty-file{len(pretty_files)}.txt", 'w', encoding="utf-8") as prettyJsFile:
            prettyJsFile.write(url + '\n') 
            prettyJsFile.write(req) 
    return req