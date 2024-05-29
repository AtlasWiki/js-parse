from utils import remove_dupes, clean_urls
def stdout_dirs(all_dirs, remove_third_parties, filter, stdout):
    remove_dupes(all_dirs)
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

def write_files(all_dirs, remove_third_parties, filter, stdout):
    remove_dupes(all_dirs)
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
    with open(f"""{target["domain"]}/parsed-urls/all_urls.txt""", "w", encoding="utf-8") as directories:
        directories.write('')
    with open(f"""{target["domain"]}/parsed-urls/all_urls.txt""", "a", encoding="utf-8") as directories:
        for unique_dir in all_dirs:
            directories.write(clean_urls(unique_dir) + '\n')