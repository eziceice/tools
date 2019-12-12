from igramscraper.instagram import Instagram
from datetime import datetime
from argparse import ArgumentParser



def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month


class Detail:
    username = ""
    total_likes = 0
    posts_in_month = {}

    def __init__(self, username, total_likes, posts_in_month):
        self.username = username
        self.total_likes = total_likes
        self.posts_in_month = posts_in_month


class InstagramAnalyzer:

    def __init__(self, username, password):
        self.instagram = Instagram()
        self._login(username, password)
        self.likes = {}
        self.month_posts = {}
        self.following_common = []

    def _login(self, username, password):
        self.instagram.with_credentials(username, password)
        self.instagram.login()

    def analyze(self, *args, **kwargs):
        for arg in args:
            medias = self.instagram.get_medias(arg, count=kwargs['count'])
            self._count_total_likes(arg, medias)
            self._count_posts_in_month(arg, medias)

    def _count_total_likes(self, username, medias):
        total_likes = 0
        for media in medias:
            total_likes += media.likes_count
        self.likes[username] = total_likes

    def _count_posts_in_month(self, username, medias):
        start = datetime.now()
        month_count = {}
        for media in medias:
            date = datetime.fromtimestamp(media.created_time)
            if diff_month(start, date) > 1:
                start = date
                month_count['%s-%s' % (date.year, date.month)] = 1
            elif diff_month(start, date) <= 1:
                if '%s-%s' % (date.year, date.month) in month_count.keys():
                    month_count['%s-%s' % (date.year, date.month)] += 1
                else:
                    month_count['%s-%s' % (date.year, date.month)] = 1
        self.month_posts[username] = month_count

    def find_following_in_common(self, *args):
        for arg in args:
            account = self.instagram.get_account(arg)
            following = self.instagram.get_following(account.identifier, 200, 100, delayed=True)['accounts']
            following_username = self._populate_following(following)
            if len(self.following_common) == 0:
                self.following_common = following_username
            else:
                self.following_common = list(set(self.following_common).intersection(following_username))


    def _populate_following(self, following):
        following_username = set()
        for account in following:
            following_username.add(account.username)
        return following_username




if __name__ == '__main__':
    # parser = ArgumentParser()
    # username = parser.add_argument('-u', '--username', help='Instagram account')
    # password = parser.add_argument('-p', '--password', help='Instagram password')
    #
    # if username or password is None:
    #     print('Username and password must be provided in the argument')
    #     raise ValueError()

    instagramAnalyzer = InstagramAnalyzer(USERNAME, PASSWORD)
    instagramAnalyzer.find_following_in_common('cocorosiekz', 'ez_ice', 'tonny_z_z')
    print(instagramAnalyzer.following_common)
    # instagramAnalyzer.analyze('cocorosiekz', count=100)
    #
    # print(instagramAnalyzer.likes)
    #
    # for user, likes in instagramAnalyzer.likes.items():
    #     print('%s\'s total likes %s' % (user, likes))
    #
    # for user, posts in instagramAnalyzer.month_posts.items():
    #     for month, month_posts in posts.items():
    #         print('%s posted %s in %s' % (user, month_posts, month))
