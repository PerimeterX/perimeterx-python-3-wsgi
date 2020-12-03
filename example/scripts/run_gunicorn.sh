#!/bin/bash
echo Starting Gunicorn.
/usr/local/bin/gunicorn sampleSite.wsgi:application --bind 0.0.0.0:8080 --workers 3
