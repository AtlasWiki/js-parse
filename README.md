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
+ **URL Filter/Check** verifies legit urls and removes false positives.
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
if running on linux do:
```
chmod +x js-parse.py
sudo mv js-parse.py /usr/local/bin/js-parse
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
or
+ linux global/binary:
```
js-parse https://youtube.com
```

## Options:
```
-h, --help            show this help message and exit
-s, --save            save prettified js files (default: False)
-b BLACKLIST [BLACKLIST ...], --blacklist BLACKLIST [BLACKLIST ...]
                      blacklist subdomains/domains (default: )
-S, --stdout          stdout friendly, displays urls only in stdout (default: False)
-m, --merge           create file and merge all urls into it (default: False)
-i, --isolate         create multiple files and store urls where they were parsed from (default: False)
```

## Some Example Usages:
basic usage:
```
python js-parse.py https://youtube.com
```
![image](https://github.com/AtlasWiki/js-parse/assets/87085506/0310f684-347f-4402-8e11-13f33b49d22b)
<br>
verify/filter urls: 
```
python js-parse.py https://youtube.com -f
```
<img width="1200" alt="image" src="https://github.com/AtlasWiki/js-parse/assets/87085506/c0c2d7f9-f667-4b48-8d20-421c9e0c0c75">


<br>

single-file: 

```
python js-parse.py https://youtube.com -m
```
![image](https://github.com/AtlasWiki/js-parse/assets/87085506/e2103af4-85b3-4a70-ac7e-d29800c5149c)
<br>

std-out: 
```
python js-parse.py https://youtube.com -S
```
<img width="718" alt="image" src="https://github.com/AtlasWiki/js-parse/assets/87085506/24408419-15b3-43e3-bcc6-755c622c0b0c">
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
