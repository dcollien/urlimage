import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import functools

try:
    from urlparse import urlparse # Python2
except ImportError:
    from urllib.parse import urlparse

try:
    from urlparse import urljoin # Python2
except ImportError:
    from urllib.parse import urljoin

SCHEMA_IMAGE = "schema_image"
OG_IMAGE = "og_image"
TWITTER_IMAGE = "twitter_image"
ICON = "icon"
FAV_ICON = "fav_icon"
APPLE_TOUCH_ICON = "apple_touch_icon"
FIRST_IMAGE = "first_image"
MS_SQUARE_70 = "ms_square_70"
MS_SQUARE_150 = "ms_square_150"
MS_SQUARE_310 = "ms_square_310"
MS_WIDE_310 = "ms_wide_310"

DEFAULT_CHECK_ORDER = [
    SCHEMA_IMAGE,
    OG_IMAGE,
    TWITTER_IMAGE,
    MS_WIDE_310,
    MS_SQUARE_310,
    APPLE_TOUCH_ICON,
    ICON,
    MS_SQUARE_150,
    MS_SQUARE_70,
    FAV_ICON,
    FIRST_IMAGE,
]

class URLNotFound(Exception):
    pass

def _absolute_url(base_url, icon_url):
    parsed_url = urlparse(icon_url)
    if not parsed_url.netloc or not parsed_url.scheme:
        return urljoin(base_url, icon_url)
    
    return icon_url

def _get_soup_from_url(url, timeout=None, headers=None, parser='html.parser'):
    res = requests.get(url, timeout=timeout, headers=headers)
    
    if res.status_code == 404:
        raise URLNotFound('The web page does not exist.')

    content = res.text

    soup = BeautifulSoup(content, parser)
    return soup

def _get_meta_content(soup, attr, value):
    for meta in soup.find_all(name='meta'):
        attr_val = meta.attrs.get(attr)
        if attr_val is not None:
            attr_val_list = [
                val.lower()
                for val in attr_val.split()
            ]
            if value.lower() in attr_val_list:
                return meta.attrs.get('content')

    return None

def _min_dimension(link):
    sizes_attr = link.attrs.get('sizes')
    if sizes_attr is None:
        return 0
    
    sizes = sizes_attr.split()
    size = sizes[0]

    if size.lower() == 'any':
        return float('inf')

    try:
        sorted_dimensions = sorted([int(x) for x in size.lower().split('x')])
    except ValueError:
        return 0
    return sorted_dimensions[0]

def _get_link_href(soup, rel):
    link_tags = []
    for link in soup.find_all(name='link'):
        rel_val = link.attrs.get('rel')
        if rel_val is not None:
            rel_val_list = [
                val.lower()
                for val in rel_val
            ]
            if rel.lower() in rel_val_list:
                link_tags.append(link)
    
    if len(link_tags) > 0:
        # find the link with the largest minimum dimension
        sorted_by_size = sorted(link_tags, key=_min_dimension, reverse=True)
        return sorted_by_size[0].attrs.get('href')

    return None

def _get_schema_image(url, soup=None):
    """
    Extract Schema (meta itemprop="image") image for the given URL
    """
    if soup is None:
        soup = _get_soup_from_url(url)
    
    icon_url = _get_meta_content(soup, 'itemprop', 'image')
    if icon_url is None:
        icon_url = _get_meta_content(soup, 'property', 'image')
    
    return icon_url

def _get_twitter_image(url, soup=None):
    """
    Extract Twitter (meta name="twitter:image") image for the given URL
    """
    if soup is None:
        soup = _get_soup_from_url(url)
    
    return _get_meta_content(soup, 'name', 'twitter:image')

def _get_og_image(url, soup=None):
    """
    Extract Open Graph (meta property="og:image") image for the given URL
    """
    if soup is None:
        soup = _get_soup_from_url(url)
    
    icon_url = _get_meta_content(soup, 'property', 'og:image:secure_url')
    if icon_url is None:
        icon_url = _get_meta_content(soup, 'property', 'og:image')
    
    return icon_url

def _get_first_image(url, soup=None):
    """
    Extract the first image for the given URL
    which is a sibling of an "h1"
    """

    if soup is None:
        soup = _get_soup_from_url(url)
    
    h1_tag = soup.find('h1')
    if h1_tag:
        first_image = h1_tag.find_next_sibling('img')
        if first_image and first_image['src'] != "":
            return first_image['src']

    return None

def _get_favicon(url, soup=None):
    """
    Look for a favicon under the domain
    """

    parsed_uri = urlparse(url)
    icon_url = '{uri.scheme}://{uri.netloc}/favicon.ico'.format(uri=parsed_uri)

    res = requests.head(icon_url)
    if res.status_code != 200:
        return None
    
    return icon_url

def _get_icon(rel, url, soup=None):
    """
    Extract an icon from the link tag
    """
    
    if soup is None:
        soup = _get_soup_from_url(url)
    
    return _get_link_href(soup, rel)

def _get_ms_icon(name, url, soup=None):
    """
    Extract Microsoft image for the given URL
    """
    if soup is None:
        soup = _get_soup_from_url(url)
    
    return _get_meta_content(soup, 'name', name)

ICON_RESOLVERS = {
    SCHEMA_IMAGE: _get_schema_image,
    OG_IMAGE: _get_og_image,
    TWITTER_IMAGE: _get_twitter_image,
    ICON: functools.partial(_get_icon, 'icon'),
    APPLE_TOUCH_ICON: functools.partial(_get_icon, 'apple-touch-icon'),
    FAV_ICON: _get_favicon,
    FIRST_IMAGE: _get_first_image,
    MS_SQUARE_70: functools.partial(_get_ms_icon, 'msapplication-square70x70logo'),
    MS_SQUARE_150: functools.partial(_get_ms_icon, 'msapplication-square150x150logo'),
    MS_SQUARE_310: functools.partial(_get_ms_icon, 'msapplication-square310x310logo'),
    MS_WIDE_310: functools.partial(_get_ms_icon, 'msapplication-wide310x150logo'),
}

def get_image_for_url(url, check_order=None):
    if not url:
        raise ValueError("Empty URL")
    
    if check_order is None:
        check_order = DEFAULT_CHECK_ORDER

    try:
        soup = _get_soup_from_url(url)
    except RequestException:
        return None

    for icon_method in check_order:
        icon_resolver = ICON_RESOLVERS[icon_method]
        icon_url = icon_resolver(url, soup)
        if icon_url is not None:
            return _absolute_url(url, icon_url)

    return None
