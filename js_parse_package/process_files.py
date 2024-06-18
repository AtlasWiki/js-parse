from tqdm import tqdm
import time
from .fetch_and_extract_files import extract_files
from .utils import parse_domain
from .store_files import store_urls
from .args import argparser


args = argparser()
target_url = args.url

def process_files_with_tqdm():
    custom_bar_format = "[[\033[94m  {desc}\033[0m: [{n}/{total} {percentage:.0f}% {bar}] \033[31mCurrent:\033[0m [{elapsed}] \033[31mRemaining:\033[0m [{remaining}]  ]]"
    total_items = len(list(extract_files(target_url)))
    pbar = tqdm(range(total_items), bar_format=custom_bar_format, desc="Extracting", unit='File', position=4, ncols=80, leave=False)

    start_time = time.time()
    scope_list = args.scope
    # with tqdm(desc="Extracting", unit='URL', total=total_items, position=4, dynamic_ncols=20, leave=True) as pbar:
    for js_file in extract_files(target_url):
        if 'http' in js_file or 'https' in js_file:
            if (parse_domain(target_url) == parse_domain(js_file)):
                tqdm.write("\033[32m[Extracted]\033[0m " + js_file + f" \033[31m[{store_urls(js_file)} URLS]\033[0m")
            else:
                try:
                    True if [True if parse_domain(js_file) in scope else False for scope in scope_list].index(True) else False
                    tqdm.write("\033[32m[Extracted]\033[0m " + js_file + f" \033[31m[{store_urls(js_file)} URLS]\033[0m")
                except:
                    tqdm.write("\033[33m[Skipped]\033[0m " + js_file)
                    
        else:
            # handles both relative files and relative urls
            if (js_file[0] != "/"): 
                js_file = "/" + js_file
                tqdm.write("\033[32m[Extracted]\033[0m " + js_file + f" \033[31m[{store_urls(target_url + js_file)} URLS]\033[0m")
            else:
                tqdm.write("\033[32m[Extracted]\033[0m " + js_file + f" \033[31m[{store_urls(target_url + js_file)} URLS]\033[0m")
                
        pbar.update(1)
            
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
