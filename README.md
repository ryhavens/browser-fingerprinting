# browser-fingerprinting

This code is an implementation of a browser fingerprinting-based
de-anonymization attack against internet users.

# Demo

https://fingerprinting-1.herokuapp.com
https://fingerprinting-2.herokuapp.com

# Core Concepts

The core concept is to create and track a fingerprint of the user using an
analytics program. 

I use the open-source fingerprintjs2 library for this
demo. The fingerprint compiles 25 feature vectors and hashes them into a
fingerprint value. This fingerprint value is then used to log user activities, 
such as clicking on ads (The "Click me" button), accessing web pages, and 
notifying the server of changes in fingerprints. 

The fingerprint is sent to the backend Flask server, which stores the information in a
MongoDB database. Any website running the JavaScript analytics program on the
front-end will be able to read from the data store and track fingerprints of 
users, even if they had never visited their website. 

In this example, fingerprints and cookies work in tandem. 

If the fingerprint changes but the cookie has not changed, the backend updates 
the fingerprint according to that cookie and stashes the old fingerprint. 

If the cookie changes or is deleted but the fingerprint has not changed, the 
backend server will log the evasion attempt and restore the proper cookie.

# Results

The fingerprint data is unique to browsers and devices. I am not simply registering
browsers, but the usage patterns of the users behind those browsers. Be wary
of nefarious tracking attempts on the internet. It is far too easy to silently
steal data.