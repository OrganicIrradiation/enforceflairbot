enforceflairbot.py
==========================

A simple Reddit bot that enforces link flair.  It initially messages the author of a submission if the post does not include link flair within 5 minutes of being posted.  After 10 additional minutes, it will leave a message and remove the post if the post is not flaired.

Requires a user account with administrative privledges for the subreddit that it moderates.  Account and subreddit information must be entered into a config.ini file.

## Requirements

    praw>=2.1.20
    python-dateutil>=2.4.1
    requests>=2.6.0
    six>=1.9.0
    update-checker>=0.11