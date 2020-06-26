# Inventory Manager

Inventory Manager is a command line tool that takes data from ip based asset inventory sources and manages the configuration of those assets in target inventory using a regular-expression-based configuration.  

Why is Inventory Manager helpful? Let's say a source of data about systems on a network exist in SCCM.  High priority servers exist in one group and low priority desktops in another.  All systems need placed in a monitoring application.  The monitoring application must send text notifications when high priority servers go down and create low priority tickets when desktops have a full drive.  The monitoring application has two buckets for different system priorties, however, would not have a way to know which systems should go into these buckets at any given time.  The need to manage systems across applications would typically result in a manual task, often resulting in inaccurate data across applications.  Inaccurate data would rendor the target application, the monitoring tool in this example, less effective.  

Inventory Manager removes this manual step by taking cues from the the source application, and based on a rule format file, automatically ensures assets are properly configured in the target application.  

# Installation

    pip -r install requirements.txt

# Implementation

- Asset sources and targets must follow the abstract classes defined, and implement the APIs of source and target applications
- Rules files created

# Usage

    ./scrape.py -h
    Usage: scrape.py [options] filename
    Options:
    --version             show program's version number and exit
    -h, --help            show this help message and exit
    -p, --print-data      Print the results of data gathering
    -k, --print-keys      Print the available keys with counts
    -d, --dry-run         Do not do anything.  Just determine what would be done and say why.
    -j JFILE, --json-file=JFILE    Optionally specify and output file for the data in json format. 

    ./apply -h
    Usage: apply.py [options] filename
    Options:
    --version             show program's version number and exit
    -h, --help            show this help message and exit
    -p, --print-data      Print the results of the data import and do nothing
    -s, --show-detail     Print the details of rules and criteria found.
    -d, --dry-run         Do not apply anything, just log what would have been done.
    -c, --csv             Do not apply anything, just run stats on what the final states should be and return a csv.
    -e EXTRA, --extra=EXTRA Comma separated additional attributes to include in csv output. Ex: lookup_fqdn, sccm_collection 

# Workflow

![Inventory Manager Workflow](/images/inventory_manager_workflow.png)

## Acknowledgments 
 
This work was produced as a university staff project and made available under an open source license with the permission of Carnegie Mellon University.
 
## License
 
The MIT License (MIT)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
