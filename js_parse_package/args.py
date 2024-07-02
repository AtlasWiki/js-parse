import argparse, os

# get_py_filename = os.path.basename(__file__)
get_py_filename = "js-parse.py"
def argparser():
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
    parser.add_argument("-s", "--stdout", help="stdout friendly, displays urls only in stdout compatibility. also known as silent mode", action="store_true")
    parser.add_argument("-f", "--filter", help="removes false positives with http probing/request methods (use at your own risk). 4xx does not include 404 and 405", choices=['all', '1xx', '2xx', '3xx', '4xx', '5xx', 'forbidden'])
    parser.add_argument("--remove-third-parties", help="does not probe third-party urls with request methods", action="store_true")
    parser.add_argument("-n", "--no-logo", help="hides logo", action="store_true")
    parser.add_argument("-r", "--requests", help="the number of concurrent/multiple requests per second (it is multiplied by 2 as it does both GET and POST) (default is set to 12 req/sec (without specifying) which would be actually 24)", type=int, default=12)
    parser.add_argument("--scope", help="specify domain names for file extraction. Extract js files from the domain(s), Ex: google.com", nargs="*")
    parser.add_argument("-j", "--json-report", help="json report/summary of all urls", choices=["all", "no-http-headers"])
    parser.add_argument("-m", "--method", help="Display method(s) options: all, only_safe, only_unsafe, GET, POST, PATCH, PUT, DELETE, OPTIONS, HEAD", nargs="+", default=['only_safe'])
    parser.add_argument("-c", "--clean", help="print all urls in absolute format. convert all relative urls to absolute", action="store_true")

    file_group = parser.add_mutually_exclusive_group()
    file_group.add_argument("-o", "--merge", help="create file and merge all urls into it", action="store_true")
    file_group.add_argument("-i", "--isolate", help="create multiple files and store urls where they were parsed from", action="store_true")

    save_group = parser.add_mutually_exclusive_group()
    save_group.add_argument("--save-one", help="merge all saved js files into one", action="store_true")
    save_group.add_argument("--save-each", help="save individual js files", action="store_true")

    args = parser.parse_args()
    if args.method:
       args.method = ",".join(args.method).split(",")
        
    return args