# plane
Was inspired from theflightwall on instagram, took some inspiration from their open-sourced code. For my purposes I do not want an LED wall so just configured it to notify me of the landing route I can see from my apartment window. 

# set up/requirements
I use four API keys. Three flight APIs: opensky network, aviationstack, and hexdb.
Aviationstack API key goes in .env, and opensky gives credentials in a json file.
For phone and watch notifications, I use pushcut-- also added URL to .env.
Aviationstack and pushcut are both paid, but have free trials and/or free usage limits.

# how to run
just run flightdatafetcher.py in terminal.
File named after the original FlightDataFetcher.cpp from TheFlightWall_OSS.