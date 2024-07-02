import asyncio, os
from .utils import(
    remove_dupes,
    clean_urls
)
from .http_probe import filter_urls
from .args import argparser
from .shared import( 
    all_dirs,
    pretty_files,
    target,
    url_locations
    )
args = argparser()


def stdout_dirs():
    remove_dupes(all_dirs)
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
    if not args.stdout:
        print("\n\n \033[34m[Extracted From]\033[0m")
        for x,y in url_locations.items():
            print(f"\033[32m[{y}]\033[0m", x)
        print("\n \033[31m[URLS]\033[0m")
    for dir in all_dirs:
        if (args.clean):
            print(clean_urls(dir))
        else:
            print(dir)
    
    

def move_stored_files():
    for prettyfile in range(1, len(pretty_files) + 1):
        source_path = os.getcwd()
        source_filename = f"pretty-file{prettyfile}.txt"
        source_file = os.path.join(source_path, source_filename)
        destination_dir = os.path.join(source_path, f"""{target["domain"]}/parsed-files""")
        destination_file = os.path.join(destination_dir, source_filename)
        os.replace(source_file, destination_file)