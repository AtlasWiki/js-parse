import argparse

class NewlineFormatter(argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    pass

def setup_args(get_py_filename, intro_logo):
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
    parser.add_argument("-r", "--remove-third-parties", help="does not probe third-party urls with request methods", action="store_true")
    parser.add_argument("-n", "--no-logo", help="hides logo", action="store_true")

    file_group = parser.add_mutually_exclusive_group()
    file_group.add_argument("-m", "--merge", help="create file and merge all urls into it", action="store_true")
    file_group.add_argument("-i", "--isolate", help="create multiple files and store urls where they were parsed from", action="store_true")
    return parser