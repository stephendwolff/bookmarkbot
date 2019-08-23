Bookmark Bot
------------

The bookmarkbot.py script opens a mailbox and iterates through new messages, uploading URLs it finds to Pinboard (https://pinboard.in)

It is run using a cronjob once a day. Currently it is reading a mailbox which contains a mailing list on ecological issues, and updating https://pinboard.in/u:peterlist

cronjob
-------

If the script is set up in a *nix home directory, with a virtualenvironment containing the python requirements, it can be run as follows:

```
0 22 * * * bookmark . /home/bookmark/venv/bookmark/bin/activate && cd /home/bookmark/bookmarkbot && python bookmarkbot.py
```

Credits
------
Ed Mitchell - for the idea and funding
