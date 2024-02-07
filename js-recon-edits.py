import re, os, requests
from bs4 import BeautifulSoup
from tqdm import tqdm

curr_url = input('input url: ')

def fetch_html(url):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'}
    req = requests.get(url, headers=headers)
    soup = BeautifulSoup(req.content, "html.parser")
    list_tags = soup.find_all('script')
    return list_tags

def extract_files(url):
    for tags in fetch_html(url):
        try: 
            js_file = tags['src']
            yield js_file
        except KeyError:
            pass

def verify_files():
    blacklist = ['googlelapis','cloudflare']
    custom_bar_format = "{desc}: {n}/{total} {percentage:.0f}% Current: {elapsed} Remaining: {remaining} "

    total_items = len(list(extract_files(curr_url)))
    for js_file in tqdm(extract_files(curr_url), desc="Extracted", unit='URL', bar_format=custom_bar_format, total=total_items, position=0, dynamic_ncols=True, leave=True):
       if any(domain in js_file for domain in blacklist):
           print('not extracted: ' + js_file)
           pass
       else:
            # checks for absolute/relative paths
            if 'http' in js_file or 'https' in js_file:
                if curr_url in js_file:
                    print(js_file, flush=True)
                    store_urls(js_file)
            else:
                print(js_file, flush=True)
                store_urls(curr_url + js_file)

def fetch_js(url):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'}
    req = requests.get(url, headers=headers).text
    return req

def extract_urls(url):
    dirs = re.findall('["\'][\w\.\?\-\_]*/[\w/\_\-\s\?\.=]*["\']*', fetch_js(url))
    unique_dirs = list(dict.fromkeys(dirs))
    unique_dirs.sort()
    return unique_dirs

def store_urls(url):
    try:
        target, file_name = re.search("(?:[a-zA-Z0-9-](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9-])?\.)+[a-zA-Z]{2,}", url).group(0), re.search("[^/]*\.js", url).group(0)
        os.mkdir(target)
        os.mkdir(target + '/parsed-js')
    except FileExistsError:
        pass
    for quoted_dir in extract_urls(url):
        dir = quoted_dir.strip('"')
        with open(f"{target}/parsed-js/{file_name}+relative-dirs.txt", "a") as directories:
            directories.write(dir + '\n')

if verify_files():
    pass
