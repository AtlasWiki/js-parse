#!/usr/bin/env python3
import re, os, requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import jsbeautifier
import argparse
import httpx
import time
import statuses


allowed_status_codes = statuses.allowed_status_codes
blocked_status_codes = statuses.blocked_status_codes
colored_status_codes = statuses.colored_status_codes
one_x_x_codes = statuses.one_x_x_codes
two_x_x_codes = statuses.two_x_x_codes
three_x_x_codes = statuses.three_x_x_codes
four_x_x_codes = statuses.four_x_x_codes
five_x_x_codes = statuses.five_x_x_codes

pretty_files = []
get_py_filename = os.path.basename(__file__)
target= ""
all_dirs=[]
intro_logo = f"""\u001b[31m

░░░░░██╗░██████╗░░░░░░██████╗░░█████╗░██████╗░░██████╗███████╗
░░░░░██║██╔════╝░░░░░░██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔════╝
░░░░░██║╚█████╗░█████╗██████╔╝███████║██████╔╝╚█████╗░█████╗░░
██╗░░██║░╚═══██╗╚════╝██╔═══╝░██╔══██║██╔══██╗░╚═══██╗██╔══╝░░
╚█████╔╝██████╔╝░░░░░░██║░░░░░██║░░██║██║░░██║██████╔╝███████╗
░╚════╝░╚═════╝░░░░░░░╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚═╝╚═════╝░╚══════╝
      




--------------------------------------------------------------\u001b[0m"""
class NewlineFormatter(argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    pass

parser = argparse.ArgumentParser(prog= f"python {get_py_filename}", description='\u001b[96mdescription: parses urls from js files', epilog=
f'''
\u001b[91mbasic usage:\u001b[0m python {get_py_filename } https://youtube.com
\u001b[91msingle file:\u001b[0m python {get_py_filename } https://youtube.com -m
\u001b[91mfilter/verify urls:\u001b[0m python {get_py_filename } https://youtube.com -f
\u001b[91mstdout:\u001b[0m python {get_py_filename } https://youtube.com -S   
''', formatter_class=NewlineFormatter, usage=f'{intro_logo}\n\u001b[32m%(prog)s [options] url\u001b[0m')

parser.add_argument("url", help="\u001b[96mspecify url with the scheme of http or https")
parser.add_argument("--save", help="save prettified js files", action="store_true")
parser.add_argument("-s", "--stdout", help="stdout friendly, displays urls only in stdout compatibility. also known as silent mode", action="store_true")
parser.add_argument("-f", "--filter", help="removes false positives with http probing/request methods (use at your own risk)", choices=['all', 'api', '1xx', '2xx', '3xx', '4xx', '5xx'])
parser.add_argument("-r", "--remove-third-parties", help="does not probe third-party urls with request methods", action="store_true")
parser.add_argument("-n", "--no-logo", help="hides logo", action="store_true")
# parser.add_argument("-k", "--kontrol", help="removes false positives with httpx/requests (use at your own risk)", choices=['ALL', 'API', '1xx', '2xx', '3xx', '4xx', '5xx'])

file_group = parser.add_mutually_exclusive_group()
file_group.add_argument("-m", "--merge", help="create file and merge all urls into it", action="store_true")
file_group.add_argument("-i", "--isolate", help="create multiple files and store urls where they were parsed from", action="store_true")

args = parser.parse_args()
target_url = args.url

if (target_url[len(target_url) - 1] == '/'):
    target_url = args.url[:len(target_url)-1]

intro_logo = f"""\u001b[31m


░░░░░██╗░██████╗░░░░░░██████╗░░█████╗░██████╗░░██████╗███████╗
░░░░░██║██╔════╝░░░░░░██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔════╝
░░░░░██║╚█████╗░█████╗██████╔╝███████║██████╔╝╚█████╗░█████╗░░
██╗░░██║░╚═══██╗╚════╝██╔═══╝░██╔══██║██╔══██╗░╚═══██╗██╔══╝░░
╚█████╔╝██████╔╝░░░░░░██║░░░░░██║░░██║██║░░██║██████╔╝███████╗
░╚════╝░╚═════╝░░░░░░░╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚═╝╚═════╝░╚══════╝
      


{('parsing webpage: ' + target_url)}

--------------------------------------------------------------\u001b[0m"""

def verify_files():
    if (args.merge or args.isolate):
        if (args.merge and args.stdout):
            process_files_without_tqdm()
            write_files()
            stdout_dirs()
        elif (args.merge):
            process_files_with_tqdm()
            write_files()
            print(f'\n\n\n\033[31m[PARSED]\033[0m {len(all_dirs)} urls\n')
        else:
            process_files_with_tqdm()
            print(f'\n\n\n\033[31m[PARSED]\033[0m {len(all_dirs)} urls\n')
    elif(args.stdout):
        process_files_without_tqdm()
        stdout_dirs()
    else:
        process_files_with_tqdm()
        stdout_dirs()
        print(f'\n\n\n\033[31m[PARSED]\033[0m {len(all_dirs)} urls\n')
    if(args.save):
        move_stored_files()
        print('saved js files')
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
        return list_tags
    except ( requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema, requests.exceptions.InvalidURL):
            print(f'NOT FOUND: invalid url, missing, or does not start with http:// or https:// in {url}')
            quit()
   
def store_urls(url):
    try:
        global target
        target, file_name = re.search("(?:[a-zA-Z0-9-](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9-])?\.)+[a-zA-Z]{2,}", url).group(0), re.search("([^/]*\.js)", url).group(0)
        parsed_js_directory_path = f"{target}/parsed-urls/"
        parsed_files_directory_path = f"{target}/parsed-files/"

        if (args.isolate or args.merge):
            try:
                os.makedirs(parsed_js_directory_path)
            except FileExistsError:
                pass
            if(args.save):
                os.mkdir(parsed_files_directory_path)

    except FileExistsError:
        pass
    except AttributeError:
        pass
   
    for quoted_dir in extract_urls(url):
        try:
            if (args.isolate):
                dir = quoted_dir.strip('"')
                with open(f"{target}/parsed-urls/{file_name}+dirs.txt", "a", encoding="utf-8") as directories:
                    directories.write(dir + '\n')
            elif (args.merge):
                dir = quoted_dir.strip('"')
                all_dirs.append(dir)
            else:
                dir = quoted_dir.strip('"')
                all_dirs.append(dir)
        finally:
             if(args.save):
                parsed_files_directory_path = f"{target}/parsed-files/"
                if not (os.path.exists(parsed_files_directory_path)):
                    os.makedirs(parsed_files_directory_path)

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

def move_stored_files():
    for prettyfile in range(1, len(pretty_files) + 1):
        source_path = os.getcwd()
        source_filename = f"pretty-file{prettyfile}.txt"
        source_file = os.path.join(source_path, source_filename)
        destination_dir = os.path.join(source_path, f"{target}/parsed-files")
        destination_file = os.path.join(destination_dir, source_filename)
        os.replace(source_file, destination_file)

def write_files():
    remove_dupes()
    if (args.remove_third_parties):
        if (args.filter and args.stdout):
            filter_urls_without_tqdm()
        elif (args.filter):
            filter_urls_with_tqdm()
        else:
            print("must have -f (filter) option with -r (remove third parties)")
            quit()
    elif (args.filter and args.stdout):
            filter_urls_without_tqdm()
    elif (args.filter):
        filter_urls_with_tqdm()
    with open(f"{target}/parsed-urls/all_urls.txt", "w", encoding="utf-8") as directories:
        directories.write('')
    with open(f"{target}/parsed-urls/all_urls.txt", "a", encoding="utf-8") as directories:
        for unique_dir in all_dirs:
            directories.write(clean_urls(unique_dir) + '\n')

def stdout_dirs():
    remove_dupes()
    if (args.remove_third_parties):
        if (args.filter and args.stdout):
            filter_urls_without_tqdm()
        elif (args.filter):
            filter_urls_with_tqdm()
        else:
            print("must have -f (filter) option with -r (remove third parties)")
            quit()
    elif (args.filter and args.stdout):
            filter_urls_without_tqdm()
    elif (args.filter):
        filter_urls_with_tqdm()
    for dir in all_dirs:
        print(clean_urls(dir))
        

def remove_dupes():
    all_dirs[:] = list(dict.fromkeys(all_dirs))

def process_files_with_tqdm():
    custom_bar_format = "[[\033[94m  {desc}\033[0m: [{n}/{total} {percentage:.0f}%] \033[31mCurrent:\033[0m [{elapsed}] \033[31mRemaining:\033[0m [{remaining}]  ]]"
    total_items = len(list(extract_files(target_url)))
    start_time = time.time()
    for js_file in tqdm(extract_files(target_url), desc="Extracting", unit='URL', bar_format=custom_bar_format, total=total_items, position=4, dynamic_ncols=True, leave=False):
        # handles absolute urls that belong to target's domain
        if 'http' in js_file or 'https' in js_file:
            if (parse_domain(target_url) == parse_domain(js_file)):
                tqdm.write("\033[32m[Extracted]\033[0m " + js_file)
                store_urls(js_file)
            else:
                tqdm.write("\033[33m[Skipped]\033[0m " + js_file)
        else:
            # handles both relative files and relative urls
            if (js_file[0] != "/"): 
                js_file = "/" + js_file
                tqdm.write("\033[32m[Extracted]\033[0m " + js_file)
                store_urls(target_url + js_file)
            else:
                tqdm.write("\033[32m[Extracted]\033[0m " + js_file)
                store_urls(target_url + js_file)
    print("")
    end_time = time.time()
    elapsed_time = end_time - start_time
    print("  \033[94m" + f"[COMPLETED]\033[0m {total_items} files in {elapsed_time:.2f} seconds")
 

def process_files_without_tqdm():
    for js_file in extract_files(target_url):
        # handles absolute urls that belong to target's domain
        if 'http' in js_file or 'https' in js_file:
            if target_url in js_file:
                store_urls(js_file)
        else:
            # handles both relative files and relative urls
            if (js_file[0] != "/"): 
                js_file = "/" + js_file
                store_urls(target_url + js_file)
            else:
                store_urls(target_url + js_file)

def filter_urls_without_tqdm():
    to_remove = []
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'}
    with httpx.Client(follow_redirects=True, headers=headers) as client:
        for dir in all_dirs[:]:
            try:
                if dir[:4] == "http":
                    formatted_dir = dir
                    if (args.remove_third_parties):
                        curr_domain = parse_domain(formatted_dir)
                        target_domain = parse_domain(args.url) 
                        if (curr_domain != target_domain):
                            formatted_dir = ""
                elif dir[0] != "/":
                    formatted_dir = args.url + f'/{dir}'
                else:
                    formatted_dir = args.url + dir

                get_response, post_response = client.get(formatted_dir), client.post(formatted_dir)
                get_status, post_status = str(get_response.status_code), str(post_response.status_code)
                get_status_verified, post_status_verified = allowed_status_codes.get(f'{get_status}', False), allowed_status_codes.get(f'{post_status}', False)
                
                # removes local/relative urls (dir not formatted dir)
                if not (get_status_verified or post_status_verified):
                   if dir[0] != "/" or dir[0] == "/":
                        to_remove.append(dir)
                else:
                    pass
                # removes absolute/http urls
            except Exception:
                #tqdm.write(f"Error processing {dir}: {e}")
                to_remove.append(dir)


    for dir in to_remove:
        all_dirs.remove(dir)
        
def filter_urls_with_tqdm():
    print('\nVerifying URLs, please wait')
    start_time = time.time()
    custom_bar_format = "[[\033[94m{desc}\033[0m: [{n}/{total} {percentage:.0f}%] \033[31mTime-Taking:\033[0m [{elapsed}] \033[31mTime-Remaining:\033[0m [{remaining}] ]]"
    total_items = len(all_dirs)
    to_remove = []
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'}
    with httpx.Client(follow_redirects=True, headers=headers) as client:
        for dir in tqdm(all_dirs[:], desc=" Probing", unit='URL', total=total_items, bar_format=custom_bar_format, position=4, dynamic_ncols=True, leave=False):
            if (dir == "https://api.wepwn.ma/contact"): 
                pass   
            else:
                try:
                    if dir[:4] == "http":
                        formatted_dir = dir
                        if (args.remove_third_parties):
                            curr_domain = parse_domain(formatted_dir)
                            target_domain = parse_domain(args.url) 
                            if (curr_domain != target_domain):
                                formatted_dir = ""
                    elif dir[0] != "/":
                        formatted_dir = args.url + f'/{dir}'
                    else:
                        formatted_dir = args.url + dir
                    # get/post requests
                    get_response, post_response = client.get(formatted_dir), client.post(formatted_dir)
                    get_status, post_status = str(get_response.status_code), str(post_response.status_code)
                    get_file_type = get_response.headers.get("Content-Type").split(";")[0]
                    # get/post messages 
                    get_status_color, post_status_color= str(colored_status_codes.get(get_status[0])), str(colored_status_codes.get(post_status[0]))
                    get_status_colored_message, post_status_colored_message =  get_status_color + get_status, post_status_color + post_status
                    # get/post conditions
                    get_status_verified, post_status_verified = allowed_status_codes.get(f'{get_status}', False), allowed_status_codes.get(f'{post_status}', False)
                    get_status_blocked = blocked_status_codes.get(f'{get_status}', False)
                    verified_four_codes_post = four_x_x_codes.get(post_status, False)
                    verified_four_codes_get = four_x_x_codes.get(get_status, False)
                    # get/post colored statements
                    reset_color = '\033[0m'
                    verified_message_strip = f"\033[33m[Verified]{reset_color} "
                    get_status_full_message = verified_message_strip + f"{get_status_color}[{get_status_colored_message}][GET]{reset_color} "
                    post_status_full_message = verified_message_strip + f"{post_status_color}[{post_status_colored_message}][POST]{reset_color} "
                    get_and_post_full_message = get_status_full_message + post_status_full_message.replace(verified_message_strip, "")
                    get_and_post_full_error_message = verified_message_strip + f"{get_status_blocked}[{get_status}][GET] [{post_status}][POST]{reset_color} "
                    
                    #
                    
                    # print(post_status)
                    # print(four_x_x_codes)
                    if (get_status_verified and post_status_verified):
                        head_status, options_status = str(client.head(formatted_dir).status_code), str(client.options(formatted_dir).status_code)
                        head_status_color, options_status_color = str(colored_status_codes.get(head_status[0])), str(colored_status_codes.get(options_status[0]))
                        head_status_colored_message, options_status_colored_message = head_status_color + head_status, options_status_color + options_status
                        head_status_verified, options_status_verified = allowed_status_codes.get(f'{head_status}', False), allowed_status_codes.get(f'{options_status}', False)
                        head_status_full_message_others = get_and_post_full_message + f"{head_status_color}[{head_status_colored_message}][HEAD]{reset_color} "
                        options_status_full_message_others = get_and_post_full_message + f"{options_status_color}[{options_status_colored_message}][OPTIONS]{reset_color} "
                        options_head_status_full_message_others = head_status_full_message_others + f"{options_status_color}[{options_status_colored_message}][OPTIONS]{reset_color} "
                        post_file_type = post_response.headers.get("Content-Type").split(";")[0]
                        verified_four_codes_head = four_x_x_codes.get(head_status, False)
                        verified_four_codes_options = four_x_x_codes.get(options_status, False)

                        if (head_status_verified and options_status_verified):
                            if(args.filter == 'all'):
                                tqdm.write(f'{options_head_status_full_message_others} \033[34m[{post_file_type}]\033[0m  {dir}')
                            elif(args.filter == '4xx'):
                                if (verified_four_codes_head and verified_four_codes_options):
                                    tqdm.write(f'{options_head_status_full_message_others} \033[34m[{post_file_type}]\033[0m  {dir}')
                                else:
                                    to_remove.append(dir)
                        elif (head_status_verified):
                            if(args.filter == 'all'):
                                tqdm.write(f'{head_status_full_message_others} \033[34m[{post_file_type}]\033[0m  {dir}')
                            elif(args.filter == '4xx'):
                                if (verified_four_codes_head):
                                    tqdm.write(f'{head_status_full_message_others} \033[34m[{post_file_type}]\033[0m  {dir}')
                                else:
                                    to_remove.append(dir)
                        elif (options_status_verified):
                            if(args.filter == 'all'):
                                tqdm.write(f'{options_status_full_message_others} \033[34m[{post_file_type}]\033[0m  {dir}')
                            elif(args.filter == '4xx'):
                                if (verified_four_codes_post and verified_four_codes_get):
                                    tqdm.write(f'{options_head_status_full_message_others} \033[34m[{post_file_type}]\033[0m  {dir}')
                                else:
                                    to_remove.append(dir)
                        else:
                            if(args.filter == 'all'):
                                tqdm.write(f'{get_and_post_full_message} \033[34m[{post_file_type}]\033[0m  {dir}')
                            elif(args.filter == '4xx'):
                                if (verified_four_codes_post):
                                    tqdm.write(f'{get_and_post_full_message} \033[34m[{post_file_type}]\033[0m  {dir}')
                                else:
                                    to_remove.append(dir)
                    
                    elif(get_status_verified):
                        if(args.filter == 'all'):
                            tqdm.write(f'{get_status_full_message} \033[34m[{get_file_type}]\033[0m  {dir}')
                        if (verified_four_codes_get):
                            tqdm.write(f'{get_status_full_message} \033[34m[{get_file_type}]\033[0m  {dir}')
                        else:
                            to_remove.append(dir)
                    elif(post_status_verified):
                        post_file_type = post_response.headers.get("Content-Type").split(";")[0]
                        if(args.filter == 'all'):
                            tqdm.write(f'{post_status_full_message} \033[34m[{post_file_type}]\033[0m  {dir}')
                        elif(args.filter == '4xx'):
                            if (verified_four_codes_post):
                                tqdm.write(f'{post_status_full_message} \033[34m[{post_file_type}]\033[0m  {dir}')
                            else:
                                to_remove.append(dir)
                    else:
                        if(args.filter == 'all'):
                            tqdm.write(f'{get_and_post_full_error_message} {dir}')
                        elif(args.filter == '4xx'):
                            if (verified_four_codes_post):
                                tqdm.write(f'{post_status_full_message} \033[34m[{post_file_type}]\033[0m  {dir}')
                            else:
                                to_remove.append(dir)
                        # removes local/relative urls
                        if dir[0] != "/" or dir[0] == "/":
                            to_remove.append(dir)
                # removes absolute/http urls
                except Exception as e:
                    # tqdm.write(f"Error processing {dir}: {e}") # for error checking
                    to_remove.append(dir)

    end_time = time.time()
    elapsed_time = end_time - start_time

    print("")
    print("  \033[94m" + f"[PROBED]\033[0m {total_items} urls in {elapsed_time:.2f} seconds")
    for dir in to_remove:
        all_dirs.remove(dir)

def clean_urls(url):
    if(url[:4] == "http"):
            
            return url
    if (url[0] != "/"):
        url = "/" + url
        return url
    else:
        return url
  
def parse_domain(http_url):
    url_pieces = http_url.split("/", 3)
    domain_labels = url_pieces[2].split(".")
    registered_domain = domain_labels[-2] + "." + domain_labels[-1] 
    return registered_domain

if __name__ == "__main__":
    if (args.stdout):
        pass
    else:
        if (args.no_logo):
            pass
        else:
            print(intro_logo)
    verify_files()
    pass