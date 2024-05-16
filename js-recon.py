import re, os, requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import jsbeautifier
pretty_files = []


curr_url = input('input url: ')

def verify_files():
    blacklist = ['google.com']
    custom_bar_format = "{desc}: {n}/{total} {percentage:.0f}% Current: {elapsed} Remaining: {remaining} "
    #total_items = list(extract_files(curr_url))
    total_items = len(list(extract_files(curr_url)))
    
    for js_file in tqdm(extract_files(curr_url), desc="Extracted", unit='URL', bar_format=custom_bar_format, total=total_items, position=0, dynamic_ncols=True, leave=True):
       if any(domain in js_file for domain in blacklist):
           print('not extracted: ' + js_file)
           pass
       else:
            if 'http' in js_file or 'https' in js_file:
                if curr_url in js_file:
                    print(js_file, flush=True)
                    store_urls(js_file)
            else:
                print(js_file, flush=True)
                store_urls(curr_url + js_file)

    if(store_files()):
        print('done')

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
    except ( requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema, requests.exceptions.InvalidURL):
            print(f'NOT FOUND: invalid url, missing, or does not start with http/https protocol in {url}')
            quit()

    req = requests.get(url, headers=headers)
    soup = BeautifulSoup(req.content, "html.parser")
    list_tags = soup.find_all('script')
    return list_tags

def store_urls(url):
    try:
        global target
        target, file_name = re.search("(?:[a-zA-Z0-9-](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9-])?\.)+[a-zA-Z]{2,}", url).group(0), re.search("([^/]*\.js)", url).group(0)
        os.mkdir(target)
        os.mkdir(target + '/parsed-urls/')
        os.mkdir(target + '/parsed-files/')

    except FileExistsError:
        pass
    except AttributeError:
        file_name = url
        return file_name
   
    for quoted_dir in extract_urls(url):
        try:
            dir = quoted_dir.strip('"')
            with open(f"{target}/parsed-urls/{file_name}+dirs.txt", "a", encoding="utf-8") as directories:
                directories.write(dir + '\n')
        except FileNotFoundError:
            directory_path = f"{target}/parsed-js/"
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)

            dir = quoted_dir.strip('"')
            file = open(f"{target}/parsed-js/{file_name}+dirs.txt", "w")
            file.close()

            with open(f"{target}/parsed-js/{file_name}+dirs.txt", "a", encoding="utf-8") as directories:
                directories.write(dir + '\n')

def extract_urls(url):
    req = fetch_js(url)
    absolute_pattern = r'(["\'])(https?://(?:www\.)?\S+?)\1'
    relative_dirs = re.findall('["\'][\w\.\?\-\_]*/[\w/\_\-\s\?\.=]*["\']*', req)
    absolute_urls = re.findall(absolute_pattern, req)
    absolute_urls = [url[1] for url in absolute_urls] 
    all_dirs = relative_dirs + absolute_urls
    unique_dirs = list(dict.fromkeys(all_dirs))
    unique_dirs.sort()
    return unique_dirs

def fetch_js(url):
    # global body_req
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'}
    req = requests.get(url, headers=headers).text
    req = jsbeautifier.beautify(req)
    pretty_files.append(url)
    # body_req = req
    # unique_pretty_files = list(dict.fromkeys(pretty_files))
    # print(pretty_files)
    with open(f"pretty-file{len(pretty_files)}.txt", 'w', encoding="utf-8") as prettyJsFile:
        prettyJsFile.write(url + '\n') 
        prettyJsFile.write(req) 
    
    return req

def store_files():
    for prettyfile in range(1, len(pretty_files) + 1):
        source_path = os.getcwd()
        source_filename = f"pretty-file{prettyfile}.txt"
        source_file = os.path.join(source_path, source_filename)
        destination_dir = os.path.join(source_path, f"{target}/parsed-files")
        destination_file = os.path.join(destination_dir, source_filename)
        os.replace(source_file, destination_file)
        # print(source_filename)
        # print(source_file)
        # print(destination_file)



    

 
        
    

    


        
if verify_files():
    pass
    



