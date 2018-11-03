# site-minify
Minify script for my website.

`config.json` format and defaults:

Remove duplicate newlines so everything is on consecutive lines:
```json
"remove_extra_newlines": true
```

Cache minified CSS files locally:
```json
"cache_css": true
```

Maximum amount of minification attempts using https://cssminifier.com:
```json
"css_minify_attempts": 10
```

HTML pages that should be minified:
```json
"pages": []
```
Other files that should be copied to the output directory.
```json
"other": []
```
