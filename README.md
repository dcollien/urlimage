# Infer an image for a given URL

## What this does:

Given the URL of a website (e.g. "https://www.mozilla.org"), it attempts to find the most appropriate image that represents this site, and returns the URL of that image.

## How it works:

The HTML of the page is parsed (BeautifulSoup) and meta/link tags are extracted which may contain clues as to which image to use. Failing this, the favicon is tried, or else it searches for the first img tag following the first h1 on the page.

The default search order is:

```
DEFAULT_CHECK_ORDER = [
    SCHEMA_IMAGE,
    OG_IMAGE,
    TWITTER_IMAGE,
    MS_WIDE_310,
    MS_SQUARE_310,
    ICON,
    APPLE_TOUCH_ICON,
    MS_SQUARE_150,
    MS_SQUARE_70,
    FAV_ICON,
    FIRST_IMAGE,
]
```

Which corresponds to:

 * meta tag with itemprop="image" or property="image"
 * meta tag with property="og:image:secure_url" or property="og:image"
 * meta tag with name="twitter:image"
 * meta tag with name="msapplication-wide310x150logo"
 * meta tag with name="msapplication-square310x310logo"
 * link tag with rel="apple-touch-icon" (if 'sizes' is provided, the link tag with the largest minimum dimension is selected)
 * link tag with rel="icon" (if 'sizes' is provided, the link tag with the largest minimum dimension is selected)
 * meta tag with name="msapplication-square150x150logo"
 * meta tag with name="msapplication-square70x70logo"
 * requesting "{scheme}://{domain}/favicon.ico" to see if it exists
 * the first img tag siblings with an h1 tag.

