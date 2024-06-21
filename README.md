# JS-Parse 
  A tool that is used for parsing urls and endpoints from javascript files.
  It extracts urls from individual js files linked to the current webpage.
  JS-Parse has a few flexible features - basic stdout, blacklisting unwanted third party js files, downloading beautified js files, organized multi-file saving, and single file saving.
  
  Created by mrunoriginal/AtlasWiki
<br>
<br>

## Key Features:
+ **Stdout-Friendly:** basic printing of only urls to stdout.
+ **Downloading:** allows you to download js files that are in a beautified format.
+ **File Management:** allows an organized structure of storing the files and urls.
+ **File Association:** parses the name of the js files and writes the associated urls to them.
+ **URL Filter/Check:** verifies legit urls and removes false positives.
+ **Disable Third Party URL Probing:** disables http requests sent to third party urls.
+ **Fast HTTP Probing**: uses concurrent requests and allow you to optionally set the requests per sec.
+ **Filtering modes**: comes with filtering of specific status codes when doing http probing.
+ **HTTP Probing Report Summary**: saves a json report summary of response status codes and header information of the urls.
+ **Method Selection**: allows you to select which methods to use. default is only_safe
<br>

## Installation:

clone the repo
```
git clone https://github.com/AtlasWiki/js-parse.git
```
install the dependencies
```
pip install -r requirements.txt
```

run the file:
+ python:
```
python js-parse.py https://youtube.com
```
or
+ linux:
```
./js-parse https://youtube.com
```


## Options:
```
-h, --help            show this help message and exit
--save                save prettified js files (default: False)
-s, --stdout          stdout friendly, displays urls only in stdout compatibility. also known as silent mode (default: False)
-f {all,1xx,2xx,3xx,4xx,5xx,forbidden}, --filter {all,1xx,2xx,3xx,4xx,5xx,forbidden}
                      removes false positives with http probing/request methods (use at your own risk). 4xx does not include 404 and 405 (default: None)
--remove-third-parties
                      does not probe third-party urls with request methods (default: False)
-n, --no-logo         hides logo (default: False)
-r REQUESTS, --requests REQUESTS
                      the number of concurrent/multiple requests per second (it is multiplied by 2 as it does both GET and POST) (default is set to 12 req/sec (without specifying) which would be actually 24) (default: 12)
--scope [SCOPE ...]   specify domain names for file extraction. Extract js files from the domain(s), Ex: google.com (default: None)
-j {all,no-http-headers}, --json-report {all,no-http-headers}
                      json report/summary of all urls (default: None)
-m METHOD [METHOD ...], --method METHOD [METHOD ...]
                      Display method(s) options: all, only_safe, only_unsafe, GET, POST, PATCH, PUT, DELETE, OPTIONS, HEAD (default: ['only_safe'])
-o, --merge           create file and merge all urls into it (default: False)
-i, --isolate         create multiple files and store urls where they were parsed from (default: False)
```

## Some Example Usages:
basic usage:
```
python js-parse.py https://youtube.com
```
<img width="1200" alt="image" src="https://github.com/AtlasWiki/js-parse/assets/87085506/698d7937-f660-46ae-8ae5-ad33e5057105">
<img width="1200" alt="image" src="https://github.com/AtlasWiki/js-parse/assets/87085506/424ba007-0328-4d96-ba9d-ddc83cb0d86f">

<br>

block third party url probing and probe target's urls: 
```
python js-parse.py https://youtube.com -f all --remove-third-parties
```
<img width="1200" alt="image" src="https://github.com/AtlasWiki/js-parse/assets/87085506/53d4ec98-be10-4a8e-93b2-be59e5b30fa6">
<img width="1200" alt="image" src="https://github.com/AtlasWiki/js-parse/assets/87085506/1e0910ae-eb71-4a85-9ef4-b27ac567a5fb">


<br>

single-file: 

```
python js-parse.py https://youtube.com -m
```
<img width="1200" alt="image" src="https://github.com/AtlasWiki/js-parse/assets/87085506/1d678b06-ab0f-4dfa-9810-a8f541a941b4">


<br>

std-out: 
```
python js-parse.py https://youtube.com -S
```
<img width="1200" alt="image" src="https://github.com/AtlasWiki/js-parse/assets/87085506/24408419-15b3-43e3-bcc6-755c622c0b0c">

<br>

full summary report:
```
python js-parse.py https://www.youtube.com -j -m -f all --remove-third-parties
```
<img width="1200" alt="image" src="https://github.com/AtlasWiki/js-parse/assets/87085506/aaf14e73-5bbd-4595-8631-53e31fe555f9">

<br>
<br>


### Warranty
The creator(s) of this tool provides no warranty or assurance regarding its performance, dependability, or suitability for any specific purpose.

The tool is furnished on an "as is" basis without any form of warranty, whether express or implied, encompassing, but not limited to, implied warranties of merchantability, fitness for a particular purpose, or non-infringement.

The user assumes full responsibility for employing this tool and does so at their own peril. The creator(s) holds no accountability for any loss, damage, or expenses sustained by the user or any third party due to the utilization of this tool, whether in a direct or indirect manner.

Moreover, the creator(s) explicitly renounces any liability or responsibility for the accuracy, substance, or availability of information acquired through the use of this tool, as well as for any harm inflicted by viruses, malware, or other malicious components that may infiltrate the user's system as a result of employing this tool.

By utilizing this tool, the user acknowledges that they have perused and understood this warranty declaration and agree to undertake all risks linked to its utilization.
  
### License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/AtlasWiki/js-parse/blob/main/LICENSE) for details.
