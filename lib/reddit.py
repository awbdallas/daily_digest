import praw
import prawcore
import sys

from tabulate import tabulate
from lib.source_interface import Source_Interface

class Reddit(Source_Interface):
    """Basically just a small wrapper for what we want around praw"""

    def __init__(self, cid, cis, cpass, cua, cuser):
        """
        Purpose: Get a praw instance of reddit
        Returns: nothing. Just populates self._reddit
        Parameter: All the fields needed to create a reddit instance
        """
        try:
            self._reddit = praw.Reddit(
                client_id=cid,
                client_secret=cis,
                password=cpass,
                user_agent=cua,
                username=cuser
            )
            assert self._reddit.user.me() == cuser

        except prawcore.exceptions.OAuthException:
            print('Credentials failure')
        except:
            print('Failure during login')

    def get_digest(self):
        """
        Purpose: Get daily digest
        Parameters: self
        Returns: text for the digest either a html table or string
        """
        try:
            table_headers = ['Post Title', 'Subreddit', 'URL', 'Post URL']
            table_data = []
            subreddits = self._get_user_subreddits()
            for subreddit in subreddits:
                posts = self._get_subreddit_time(subreddit)
                for post in posts:
                    table_data.append([
                        post.title,
                        subreddit.display_name,
                        post.url,
                        post.shortlink
                    ])
            return tabulate(table_data, table_headers, tablefmt='html')
        except:
            return "Failed to get reddit information"

    def _get_subreddit(self, subreddit):
        """Get a subreddit. Just need a string name"""
        try:
            sub = self._reddit.get_subreddit(subreddit, fetch=True)
            return sub
        except:
            print('Error getting subreddit {}'.format(subreddit))

    def _get_subreddit_hot(self, subreddit, number_of_posts=3):
        """
        Purpose: Get a subreddits posts for hot
        Parameters: self, subreddit instance, and a number of posts
        Returns: Number of posts based on numbers that's passed
        That wont include stickied posts
        """
        if isinstance(subreddit, str):
            self._get_subreddit(subreddit)
        elif isinstance(subreddit, praw.models.Subreddit):
            posts = []
            # giving a buffer to account for stickied
            for submission in subreddit.hot(limit=number_of_posts + 5):
                if len(posts) == number_of_posts:
                    break
                elif submission.stickied:
                    continue
                else:
                    posts.append(submission)
            assert number_of_posts == len(posts),\
                'Invalid amount of posts. Only {} out of {}'.format(
                    number_of_posts, len(posts)
                )
            return posts
        else:
            raise TypeError('{} invalid type. Must be str or subreddit'\
                    .format(type(subreddit)))

    def _get_subreddit_time(self, subreddit, number_of_posts=3, time='day'):
        """
        Purpose: Get a subreddits posts for all time
        Parameters: self, subreddit instance, number_of_posts, time
        Returns: Number of posts based on numbers that's passed
        That wont include stickied posts
        """
        posts = []
        # giving a buffer to account for stickied
        for submission in subreddit.top(time, limit=number_of_posts + 5):
            if len(posts) == number_of_posts:
                break
            elif submission.stickied:
                continue
            else:
                posts.append(submission)
        return posts

    def _get_user_subreddits(self):
        """
        Purpose: Need users subreddits
        Parameters: Self
        Returns: subreddit instance of every self-subscribed subreddits
        (doesn't include default subreddits)
        """
        assert self._reddit
        return [subreddit for subreddit in self._reddit.user.subreddits()]
