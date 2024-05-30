#!/usr/bin/env python3
import re, os, requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import jsbeautifier
import argparse
import httpx
import time
import statuses
import asyncio
# import logging

allowed_status_codes = statuses.allowed_status_codes
blocked_status_codes = statuses.blocked_status_codes
colored_status_codes = statuses.colored_status_codes
one_x_x_codes = statuses.one_x_x_codes
two_x_x_codes = statuses.two_x_x_codes
three_x_x_codes = statuses.three_x_x_codes
four_x_x_codes = statuses.four_x_x_codes
five_x_x_codes = statuses.five_x_x_codes
forbidden_x_x_codes = statuses.forbidden_x_x_codes

pretty_files = []
get_py_filename = os.path.basename(__file__)
target= {}
all_dirs=[]
to_remove = []
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
parser.add_argument("-f", "--filter", help="removes false positives with http probing/request methods (use at your own risk). 4xx does not include 404 and 405", choices=['all', '1xx', '2xx', '3xx', '4xx', '5xx', 'forbidden'])
parser.add_argument("--remove-third-parties", help="does not probe third-party urls with request methods", action="store_true")
parser.add_argument("-n", "--no-logo", help="hides logo", action="store_true")
parser.add_argument("-r", "--requests", help="the number of concurrent/multiple requests per second (it is multiplied by 2 as it does both GET and POST) (default is set to 12 req/sec which would be actually 24)", type=int, default=12)
parser.add_argument("--scope", help="specify domain names for file extraction. Extract js files from the domain(s), Ex: google.com", nargs="*")

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
        target["domain"], file_name = re.search("(?:[a-zA-Z0-9-](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9-])?\.)+[a-zA-Z]{2,}", url).group(0), re.search("([^/]*\.js)", url).group(0)
        parsed_js_directory_path = f"""{target["domain"]}/parsed-urls/"""
        parsed_files_directory_path = f"""{target["domain"]}/parsed-files/"""

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
                with open(f"""{target["domain"]}/parsed-urls/{file_name}+dirs.txt""", "a", encoding="utf-8") as directories:
                    directories.write(dir + '\n')
            elif (args.merge):
                dir = quoted_dir.strip('"')
                all_dirs.append(dir)
            else:
                dir = quoted_dir.strip('"')
                all_dirs.append(dir)
        finally:
             if(args.save):
                parsed_files_directory_path = f"""{target["domain"]}/parsed-files/"""
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
        destination_dir = os.path.join(source_path, f"""{target["domain"]}/parsed-files""")
        destination_file = os.path.join(destination_dir, source_filename)
        os.replace(source_file, destination_file)

def write_files():
    remove_dupes()
    if (args.remove_third_parties):
        if (args.filter and args.stdout):
            asyncio.run(filter_urls())
        elif (args.filter):
            asyncio.run(filter_urls())
        else:
            print("must have -f (filter) option with --remove-third-parties")
            quit()
    elif (args.filter and args.stdout):
            asyncio.run(filter_urls())
    elif (args.filter):
        asyncio.run(filter_urls())
    with open(f"""{target["domain"]}/parsed-urls/all_urls.txt""", "w", encoding="utf-8") as directories:
        directories.write('')
    with open(f"""{target["domain"]}/parsed-urls/all_urls.txt""", "a", encoding="utf-8") as directories:
        for unique_dir in all_dirs:
            directories.write(clean_urls(unique_dir) + '\n')

def stdout_dirs():
    remove_dupes()
    if (args.remove_third_parties):
        if (args.filter and args.stdout):
            asyncio.run(filter_urls())
        elif (args.filter):
            asyncio.run(filter_urls())
        else:
            print("must have -f (filter) option with --remove-third-parties")
            quit()
    elif (args.filter and args.stdout):
        asyncio.run(filter_urls())
    elif (args.filter):
        asyncio.run(filter_urls())
    for dir in all_dirs:
        print(clean_urls(dir))
        

def remove_dupes():
    all_dirs[:] = list(dict.fromkeys(all_dirs))

def process_files_with_tqdm():
    custom_bar_format = "[[\033[94m  {desc}\033[0m: [{n}/{total} {percentage:.0f}%] \033[31mCurrent:\033[0m [{elapsed}] \033[31mRemaining:\033[0m [{remaining}]  ]]"
    total_items = len(list(extract_files(target_url)))
    start_time = time.time()
    scope_list = args.scope
    for js_file in tqdm(extract_files(target_url), desc="Extracting", unit='URL', bar_format=custom_bar_format, total=total_items, position=4, dynamic_ncols=True, leave=False):
        # handles absolute urls that belong to target's domain
        if 'http' in js_file or 'https' in js_file:
            if (parse_domain(target_url) == parse_domain(js_file)):
                store_urls(js_file)
                tqdm.write("\033[32m[Extracted]\033[0m " + js_file)
            else:
                try:
                    True if [True if parse_domain(js_file) in scope else False for scope in scope_list].index(True) else False
                    store_urls(js_file)
                    tqdm.write("\033[32m[Extracted]\033[0m " + js_file)
                except:
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
    scope_list = args.scope
    for js_file in extract_files(target_url):
        # handles absolute urls that belong to target's domain
        if 'http' in js_file or 'https' in js_file:
            if (parse_domain(target_url) == parse_domain(js_file)):
                store_urls(js_file)
            else:
                try:
                    True if [True if parse_domain(js_file) in scope else False for scope in scope_list].index(True) else False
                    store_urls(js_file)
                except:
                    pass
        else:
            # handles both relative files and relative urls
            if (js_file[0] != "/"): 
                js_file = "/" + js_file
                store_urls(target_url + js_file)
            else:
                store_urls(target_url + js_file)

# logging.basicConfig(level=logging.INFO, format='%(message)s')
# logger = logging.getLogger()

def format_dir(dir):
    if (dir == "https://api.wepwn.ma/contact"): 
        pass   
    else:
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
    return formatted_dir

# all_dirs_lock = asyncio.Lock()

async def fetch_dir(client, dir):
    try:
        # get/post requests
        get_response, post_response = await client.get(format_dir(dir)), await client.post(format_dir(dir))
        get_status, post_status = str(get_response.status_code), str(post_response.status_code)
        get_file_type, post_file_type = '', ''

        try:
            get_file_type = get_response.headers.get("Content-Type").split(';')[0]
        except: 
            get_file_type = get_response.headers.get("Content-Type")
        try:
            post_file_type = post_response.headers.get("Content-Type").split(';')[0]
        except: 
            post_file_type = post_response.headers.get("Content-Type")
            

        # get/post messages
        if not (args.stdout): 
            get_status_color, post_status_color= str(colored_status_codes.get(get_status[0])), str(colored_status_codes.get(post_status[0]))
            get_status_colored_message, post_status_colored_message =  get_status_color + get_status, post_status_color + post_status
        # get/post conditions
        get_status_verified, post_status_verified = allowed_status_codes.get(f'{get_status}', False), allowed_status_codes.get(f'{post_status}', False)
        get_status_blocked = blocked_status_codes.get(f'{get_status}', False)
        verified_one_codes_post, verified_one_codes_get = one_x_x_codes.get(post_status, False), one_x_x_codes.get(get_status, False)
        verified_two_codes_post, verified_two_codes_get = two_x_x_codes.get(post_status, False), two_x_x_codes.get(get_status, False)
        verified_three_codes_post, verified_three_codes_get = three_x_x_codes.get(post_status, False), three_x_x_codes.get(get_status, False)
        verified_four_codes_post, verified_four_codes_get = four_x_x_codes.get(post_status, False), four_x_x_codes.get(get_status, False)
        verified_five_codes_post, verified_five_codes_get = five_x_x_codes.get(post_status, False), five_x_x_codes.get(get_status, False)
        verified_forbidden_code_post, verified_forbidden_code_get =  forbidden_x_x_codes.get(post_status, False), forbidden_x_x_codes.get(get_status, False)
        # get/post colored statements
        if not (args.stdout):
            reset_color = '\033[0m'
            verified_message_strip = f"\033[33m[Verified]{reset_color} "
            get_status_full_message = verified_message_strip + f"{get_status_color}[{get_status_colored_message}][GET]{reset_color} "
            post_status_full_message = verified_message_strip + f"{post_status_color}[{post_status_colored_message}][POST]{reset_color} "
            get_and_post_full_message = get_status_full_message + post_status_full_message.replace(verified_message_strip, "")
            get_and_post_full_error_message = verified_message_strip + f"{get_status_blocked}[{get_status}][GET] [{post_status}][POST]{reset_color} "
        
        
        if (args.filter=='1xx'):
            get_status_verified = verified_one_codes_get
            post_status_verified = verified_one_codes_post
        elif (args.filter=='2xx'):
            get_status_verified = verified_two_codes_get
            post_status_verified = verified_two_codes_post
        elif (args.filter=='3xx'):
            get_status_verified = verified_three_codes_get
            post_status_verified = verified_three_codes_post
        elif (args.filter == '4xx'):
            get_status_verified = verified_four_codes_get
            post_status_verified = verified_four_codes_post
        elif (args.filter == '5xx'):
            get_status_verified = verified_five_codes_get
            post_status_verified = verified_five_codes_post
        elif (args.filter=='forbidden'):
            post_status_verified = verified_forbidden_code_post
            get_status_verified = verified_forbidden_code_get

        if (get_status_verified and post_status_verified):
            head_response, options_response = await client.head(format_dir(dir)), await client.options(format_dir(dir))
            head_status, options_status =  str(head_response.status_code),str(options_response.status_code)
            if not (args.stdout):
                head_status_color, options_status_color = str(colored_status_codes.get(head_status[0])), str(colored_status_codes.get(options_status[0]))
                head_status_colored_message, options_status_colored_message = head_status_color + head_status, options_status_color + options_status
                head_status_verified, options_status_verified = allowed_status_codes.get(f'{head_status}', False), allowed_status_codes.get(f'{options_status}', False)
                head_status_full_message_others = get_and_post_full_message + f"{head_status_color}[{head_status_colored_message}][HEAD]{reset_color} "
                options_status_full_message_others = get_and_post_full_message + f"{options_status_color}[{options_status_colored_message}][OPTIONS]{reset_color} "
                options_head_status_full_message_others = head_status_full_message_others + f"{options_status_color}[{options_status_colored_message}][OPTIONS]{reset_color} "

            if (head_status_verified and options_status_verified):
                if not (args.stdout):
                    tqdm.write(f'{options_head_status_full_message_others} \033[34m[{get_file_type}]\033[0m  {dir}')

            elif (head_status_verified):
                if not (args.stdout):
                    tqdm.write(f'{head_status_full_message_others} \033[34m[{get_file_type}]\033[0m  {dir}')
    
            elif (options_status_verified):
                if not (args.stdout):
                    tqdm.write(f'{options_status_full_message_others} \033[34m[{get_file_type}]\033[0m  {dir}')
            else:
                if not (args.stdout):
                    tqdm.write(f'{get_and_post_full_message} \033[34m[{get_file_type}]\033[0m  {dir}')

        elif(get_status_verified):
            if not (args.stdout):
                tqdm.write(f'{get_status_full_message} \033[34m[{get_file_type}]\033[0m  {dir}')

        elif(post_status_verified):
            if not (args.stdout):
                tqdm.write(f'{post_status_full_message} \033[34m[{post_file_type}]\033[0m  {dir}')
            

        else:
            if (args.filter == "all"):
                if not (args.stdout):
                    tqdm.write(f'{get_and_post_full_error_message} {dir}')

            if dir[0] != "/" or dir[0] == "/":
                to_remove.append(dir)
    
    except Exception as e:
        # tqdm.write(f"Error processing {dir}: {e}") # for error checking
        to_remove.append(dir)

    
async def filter_urls():
    print('\nVerifying URLs, please wait')
    start_time = time.time()
    custom_bar_format = "[[\033[94m{desc}\033[0m: [{n}/{total} {percentage:.0f}%] \033[31mTime-Taking:\033[0m [{elapsed}] \033[31mTime-Remaining:\033[0m [{remaining}] ]]"
    total_dir_counts = len(all_dirs)
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'}
    tasks = []
    batch_size = args.requests
    if not (args.stdout):
        async with httpx.AsyncClient(follow_redirects=True, headers=headers) as client:
            with tqdm(total=total_dir_counts, desc=" Probing", unit='URL', bar_format=custom_bar_format, position=4, dynamic_ncols=True, leave=False) as pbar:
                for dir_count in range(0, total_dir_counts, batch_size):
                    # Calculate the end index for the current batch
                    end_index = min(dir_count + batch_size, total_dir_counts)
                    
                    for index in range(dir_count, end_index):
                        if index < len(all_dirs):
                            tasks.append(fetch_dir(client, all_dirs[index]))

                    # Run all tasks concurrently for the current batch
                    for task in asyncio.as_completed(tasks):
                        await task
                        pbar.update(1)  # Update the progress bar for each completed task
                    
                    tasks = []  # Clear the tasks list for the next batch
       
       
        end_time = time.time()
        elapsed_time = end_time - start_time

        print("")
        print("  \033[94m" + f"[PROBED]\033[0m {total_dir_counts} urls in {elapsed_time:.2f} seconds\n")

        
    else:
        async with httpx.AsyncClient(follow_redirects=True, headers=headers) as client:
            for dir_count in range(0, total_dir_counts, batch_size):
                # Calculate the end index for the current batch
                end_index = min(dir_count + batch_size, total_dir_counts)
                
                for index in range(dir_count, end_index):
                    if index < len(all_dirs):
                        tasks.append(fetch_dir(client, all_dirs[index]))

                # Run all tasks concurrently for the current batch
                for task in asyncio.as_completed(tasks):
                    await task

                tasks = []  # Clear the tasks list for the next batch

    for dirs in to_remove:
            all_dirs.remove(dirs)

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
