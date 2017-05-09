import os
import sys
import argparse
import json
import requests
import re

VERSION = '0.4'

CONFIG_FILE = 'config.json'
DEFAULT_CONFIG = {
    'remove_extra_newlines': True,
    'cache_css': True,
    'pages': [],
    'other': [],
}
MINIFY_URL = 'https://cssminifier.com/raw'

def exit_with_message(text, prefix='> Error: ', code=1):
    print(prefix + text)
    sys.exit(code)

parser = argparse.ArgumentParser(prog='siteminify', description='Minify static websites')
parser.add_argument('path', nargs='?', default=os.getcwd(), help='the directory where the site lives')
parser.add_argument('-o', '--out', dest='out', required=False, help='the output directory')
parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + VERSION)

args = parser.parse_args()

# Check base path

base_path = args.path

if not os.path.isdir(base_path):
    exit_with_message('"{}" is not a directory'.format(base_path))

# Check out path

out_path = os.path.join(base_path, 'out')

if args.out:
    out_path = args.out

if not os.path.exists(out_path):
    print('- Creating output directory')
    os.mkdir(out_path)
else:
    print('- Cleaning output directory')
    for entry in os.scandir(out_path):
        print('  * ' + entry.name)
        os.remove(entry.path)

print('- Done')

# Check config

config_path = os.path.join(base_path, CONFIG_FILE)

if not os.path.exists(config_path):
    with open(config_path, 'w') as f:
        json.dump(DEFAULT_CONFIG, f, indent=4)

with open(config_path, 'r') as f:
    config = json.load(f)

if not config:
    exit_with_message('config could not be loaded')

#------------

def embedded_style(minified_css):
    return '<style type="text/css">{}</style>'.format(minified_css)

def minify(css_file_path):
    with open(css_file_path, 'r') as f:
        css_content = f.read()

    if not css_content:
        return None

    response = requests.post(MINIFY_URL, data={'input': css_content})
    return response.text

linked_style_regex = re.compile(r'<link rel="stylesheet" href="([^"]+)" type="text/css">')

def main():
    print('- Minifying pages')

    for page_file_name in config['pages']:
        print('  * ' + page_file_name)

        with open(os.path.join(base_path, page_file_name), 'r') as f:
            pass

if __name__ == '__main__':
    main()
