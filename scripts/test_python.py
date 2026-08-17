import urllib.request
import os

url = "https://upload.wikimedia.org/wikipedia/commons/c/c3/Python-logo-notext.svg"
# Let's download a PNG version since PIL can't read SVG easily
url_png = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/400px-Python-logo-notext.svg.png"
urllib.request.urlretrieve(url_png, "python-icon-source.png")
