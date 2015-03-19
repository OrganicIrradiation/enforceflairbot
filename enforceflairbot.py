from ConfigParser import SafeConfigParser
import cPickle
from datetime import datetime
from dateutil.relativedelta import relativedelta
import praw
import os
import time

def save_hist(data, path):
    with open(path, 'wb') as f:
        cPickle.dump(data, f)
        
def load_hist(path):
    if os.path.isfile(path):
        with open(path, 'rb') as f:
            return cPickle.load(f)
    else:
        return {}
        
# Get the user information from the configuration file
config = SafeConfigParser()
config.read('config.ini')

reddit_username = config.get('reddit', 'username')
reddit_password = config.get('reddit', 'password')
reddit_user_agent = config.get('reddit', 'user_agent')

print 'Loading history'
tracked_submissions = load_hist('enforceflairbot_history.p')

print 'Logging into Reddit'
r = praw.Reddit(user_agent=reddit_user_agent)
r.login(reddit_username, reddit_password)

while True:
    print 'Running bot: {0}'.format(datetime.utcnow())
    # Add new submissions
    subreddit = r.get_subreddit(config.get('reddit', 'subreddit'))
    for submission in subreddit.get_new(limit=10):
        if submission.id not in tracked_submissions:
            dict_out = {}
            dict_out['author'] = submission.author.name
            dict_out['title'] = submission.title
            dict_out['short_link'] = submission.short_link
            dict_out['link_flair_text'] = submission.link_flair_text
            dict_out['created_utc'] = datetime.utcfromtimestamp(submission.created_utc)
            dict_out['messaged'] = False
            dict_out['deleted'] = False
            tracked_submissions[submission.id] = dict_out
            
    save_hist(tracked_submissions, 'enforceflairbot_history.p')

    for submission_id, submission in tracked_submissions.iteritems():
        if submission['link_flair_text']:
            # Submission had link flair, continue to the next
            continue
        if submission['deleted']:
            # Submission was already deleted, continue to the next
            continue
        if datetime.utcnow() > (submission['created_utc'] + relativedelta(hours=24)):
            # >24 hours have passed, ignore and continue to the next
            continue
            
        s = r.get_submission(submission_id=submission_id)
        submission['link_flair_text'] = s.link_flair_text

        if not submission['link_flair_text']:
            
            if datetime.utcnow() > (submission['created_utc'] + relativedelta(minutes=5)) and not submission['messaged']:
                print 'Over 5 minutes have passed, message user for submission {0}'.format(submission['short_link'])
                r.send_message(recipient=s.author, subject='Add link flair within 10 minutes or submission will be removed', message='Please add subreddit-approved link flair to [this post]({0}), otherwise it will be automatically removed in 10 minutes.'.format(submission['short_link']))
                submission['messaged'] = datetime.utcnow()
                    
            if submission['messaged'] and datetime.utcnow() > (submission['messaged'] + relativedelta(minutes=10)):
                print '10 minutes have passed since message, delete submission {0}'.format(submission['short_link'])
                s.add_comment('This submission has been removed because it was not appropriately flaired.  If you feel that this removal was in error, please message the moderators.')
                s.remove(spam=False)
                submission['deleted'] = datetime.utcnow()
                
        save_hist(tracked_submissions, 'enforceflairbot_history.p')

    time.sleep(300)
