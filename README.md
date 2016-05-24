Some code to make a train go by on the screen when a train goes by
outside. Also known as "the internet of things".

## Getting started

This project depends on
[a nice python wrapper](https://github.com/iandees/ctaapi) for the CTA
Train Tracker API, which you can install by running `pip install -r
requirements.txt`.

You'll also need to make a file called `settings.py` in the repository
root that contains your secret API key for the CTA train tracker, like
this:

```python
CTA_API_KEY = 'your-key-goes-here'
```

You can get an API key for the CTA by applying
[here](http://www.transitchicago.com/developers/traintrackerapply.aspx).

Now everything is set up! You can run `update_json.py` and it will
query the API and make a new file in `web/data/train-times.json` that
contains the data needed for the web site to make trains rumble by.

To see the website, change to the `web/` directory and run `python -m
SimpleHTTPServer` to start a web server. Visit http:://localhost:8000
and behold the trains.
