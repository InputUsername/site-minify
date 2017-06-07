import os
import sys
import argparse
import json
import requests
import re
import shutil

VERSION = '0.4'

CONFIG_FILE = 'config.json'
DEFAULT_CONFIG = {
    'remove_extra_newlines': True,
    'cache_css': True,
    'css_minify_attempts': 10,
    'pages': [],
    'other': [],
}
MINIFY_URL = 'https://cssminifier.com/raw'

def exit_with_message(text, prefix='# Error: ', code=1):
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
    CONFIG = json.load(f)

if not CONFIG:
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

def minify_and_replace(match):
    css_file = match.group(1)

    css_file_path = os.path.join(base_path, css_file)
    css_cache_path = os.path.join(out_path, css_file + '.cache')

    if os.path.exists(css_cache_path):
        print('     * Found cached css file ' + css_file)
        with open(css_cache_path, 'r') as f:
            return embedded_style(f.read())

    minified_css = None
    attempts = 0

    while not minified_css:
        if attempts > CONFIG['css_minify_attempts']:
            print('     * Minification of {} took more than {} tries. Retry? y/n'.format(css_file, CONFIG['css_minify_attempts']))
            retry = input('     >')
            if retry.lower() == 'y':
                attempts = 0
            else:
                return ''

        minified_css = minify(css_file_path)
        attempts += 1

    if CONFIG['cache_css']:
        print('     * Caching css file ' + css_file)
        with open(css_cache_path, 'w') as f:
            f.write(minified_css)

    return embedded_style(minified_css)

tab_return_regex = re.compile(r'[\t\r]')
newline_regex = re.compile(r'\n{2,}')
linked_style_regex = re.compile(r'<link rel="stylesheet" href="([^"]+)" type="text/css">')

def main():
    print('- Minifying pages')

    for page_file_name in CONFIG['pages']:
        print('  * ' + page_file_name)

        with open(os.path.join(base_path, page_file_name), 'r') as f:
            html_content = f.read()

            html_content = re.sub(tab_return_regex, '', html_content)

            if CONFIG['remove_extra_newlines']:
                html_content = re.sub(newline_regex, '\n', html_content)

            html_content = re.sub(linked_style_regex, minify_and_replace, html_content)

            with open(os.path.join(out_path, page_file_name), 'w') as o:
                o.write(html_content)

    print('- Copying other files')

    for other_file_name in CONFIG['other']:
        print('  * ' + other_file_name)

        shutil.copyfile(os.path.join(base_path, other_file_name), os.path.join(out_path, other_file_name))

    print('- Done')

if __name__ == '__main__':
    main()
