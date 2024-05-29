from statuses import (
    allowed_status_codes, 
    blocked_status_codes, 
    colored_status_codes, 
    one_x_x_codes, 
    two_x_x_codes, 
    three_x_x_codes, 
    four_x_x_codes, 
    five_x_x_codes, 
    forbidden_x_x_codes
)

def filter_urls_with_tqdm(all_dirs, remove_third_parties, url):
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
                        head_status, options_status = str(client.head(formatted_dir).status_code), str(client.options(formatted_dir).status_code)
                        head_status_color, options_status_color = str(colored_status_codes.get(head_status[0])), str(colored_status_codes.get(options_status[0]))
                        head_status_colored_message, options_status_colored_message = head_status_color + head_status, options_status_color + options_status
                        head_status_verified, options_status_verified = allowed_status_codes.get(f'{head_status}', False), allowed_status_codes.get(f'{options_status}', False)
                        head_status_full_message_others = get_and_post_full_message + f"{head_status_color}[{head_status_colored_message}][HEAD]{reset_color} "
                        options_status_full_message_others = get_and_post_full_message + f"{options_status_color}[{options_status_colored_message}][OPTIONS]{reset_color} "
                        options_head_status_full_message_others = head_status_full_message_others + f"{options_status_color}[{options_status_colored_message}][OPTIONS]{reset_color} "

                        if (head_status_verified and options_status_verified):
                            tqdm.write(f'{options_head_status_full_message_others} \033[34m[{get_file_type}]\033[0m  {dir}')

                        elif (head_status_verified):
                            tqdm.write(f'{head_status_full_message_others} \033[34m[{get_file_type}]\033[0m  {dir}')
                
                        elif (options_status_verified):
                            tqdm.write(f'{options_status_full_message_others} \033[34m[{get_file_type}]\033[0m  {dir}')
                        else:
                            tqdm.write(f'{get_and_post_full_message} \033[34m[{get_file_type}]\033[0m  {dir}')

                    elif(get_status_verified):
                        tqdm.write(f'{get_status_full_message} \033[34m[{get_file_type}]\033[0m  {dir}')

                    elif(post_status_verified):
                        tqdm.write(f'{post_status_full_message} \033[34m[{post_file_type}]\033[0m  {dir}')
                     
    
                    else:
                        if (args.filter=="all"):
                            tqdm.write(f'{get_and_post_full_error_message} {dir}')

                        if dir[0] != "/" or dir[0] == "/":
                            to_remove.append(dir)
                  
                # removes absolute/http urls
                except Exception as e:
                    # tqdm.write(f"Error processing {dir}: {e}") # for error checking
                    to_remove.append(dir)

    end_time = time.time()
    elapsed_time = end_time - start_time

    print("")
    print("  \033[94m" + f"[PROBED]\033[0m {total_items} urls in {elapsed_time:.2f} seconds\n")

    for dir in to_remove:
        all_dirs.remove(dir)