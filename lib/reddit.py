import praw
import prawcore

class Reddit(object):
    """Basically just a small wrapper for what we want around praw"""
    def __init__(self, cid, cis, cpass, cua, cuser):
        try:
            self.reddit = praw.Reddit(
                client_id=cid,
                client_secret=cis,
                password=cpass,
                user_agent=cua,
                username=cuser
            )
            assert self.reddit.user.me() == cuser

        except prawcore.exceptions.OAuthException:
            print('Credentials failure')
        except:
            print('Failure during login')

    def get_subreddit(self, subreddit):
        assert self.reddit
        try:
            sub = self.reddit.get_subreddit(subreddit, fetch=True)
            return sub
        except:
            print('Error getting subreddit {}'.format(subreddit))

    def get_subreddit_hot(self, subreddit, number_of_posts=5):
        assert self.reddit

        if isinstance(subreddit, str):
            self.get_subreddit(subreddit)
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
            raise TypeError('{} invalid type. Must be str or subreddit'.format(type(subreddit)))

    def get_subreddit_alltime(self, subreddit, number_of_posts=5):
        # checking if name or if by type isntance
        assert self.reddit

        if isinstance(subreddit, str):
            self.get_subreddit(subreddit)
        elif isinstance(subreddit, praw.models.Subreddit):
            # giving a buffer to account for stickied
            posts = []

            for submission in subreddit.top('all', limit=number_of_posts + 5):
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
            raise TypeError('{} is wrong type for this'.format(type(subreddit)))

    def get_user_subreddits(self):
        """Gives an instance of each subreddit...well of reddit base, but yeah"""
        assert self.reddit
        return [subreddit for subreddit in self.reddit.user.subreddits()]
