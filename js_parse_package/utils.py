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

def remove_dupes(all_dirs):
    all_dirs[:] = list(dict.fromkeys(all_dirs))