#!/usr/bin/env python3
from js_parse_package.args import argparser 
from js_parse_package.process_files import(
    process_files_with_tqdm,
    process_files_without_tqdm
)
from js_parse_package.show_results import(
   stdout_dirs,
   move_stored_files
)
from js_parse_package.store_files import write_files
from js_parse_package.show_results import all_dirs
# import logging
args = argparser() 
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
    elif (args.json_report):
            print('cannot use -j/--json-report alone. must pair this up with -o/--merge option')
            quit()
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
