import operator

from igramscraper.instagram import Instagram
from datetime import datetime
import requests
import json
import numpy as np
import matplotlib.pyplot as plt
from argparse import ArgumentParser


def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month


def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct * total / 100.0))
        return '{p:.2f}%  ({v:d})'.format(p=pct, v=val)
    return my_autopct


class InstagramAnalyzer:

    def __init__(self, username, password):
        self.instagram = Instagram()
        self._login(username, password)
        self.likes = {}
        self.month_posts = {}
        self.shared_followings = []
        self.likes_contributors = {}

    def _login(self, username, password):
        self.instagram.with_credentials(username, password)
        self.instagram.login()

    def analyze(self, args, **kwargs):
        for arg in args:
            if len(args) != 1:
                self._find_shared_following(arg)
            medias = self.instagram.get_medias(arg, count=kwargs['count'])
            self._count_total_likes(arg, medias)
            self._count_posts_in_month(arg, medias)
            self._count_likes_contributor(arg, medias)

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
            year_month = f'{date.year}-{date.month}'
            if diff_month(start, date) > 1:
                start = date
                month_count[year_month] = 1
            elif diff_month(start, date) <= 1:
                if year_month in month_count.keys():
                    month_count[year_month] += 1
                else:
                    month_count[year_month] = 1
        self.month_posts[username] = month_count

    def _count_likes_contributor(self, arg, medias):
        contributor_likes = {}
        for media in medias:
            accounts = self.instagram.get_media_likes_by_code(
                media.short_code, 40)['accounts']
            for account in accounts:
                key = account.username
                if arg not in self.likes_contributors.keys():
                    self.likes_contributors[arg] = {}
                if key not in contributor_likes.keys():
                    contributor_likes[key] = 1
                else:
                    contributor_likes[key] += 1
        contributor_likes = dict(
            sorted(contributor_likes.items(), key=operator.itemgetter(1), reverse=True)[:5])
        self.likes_contributors[arg] = contributor_likes

    def _find_shared_following(self, arg):
        account = self.instagram.get_account(arg)
        following = self.instagram.get_following(
            account.identifier, 200, 100, delayed=True)['accounts']
        following_username = self._populate_following_username(following)
        if len(self.shared_followings) == 0:
            self.shared_followings = following_username
        else:
            self.shared_followings = list(
                set(self.shared_followings).intersection(following_username))

    @staticmethod
    def _populate_following_username(following):
        following_username = set()
        for account in following:
            following_username.add(account.username)
        return following_username


class InstagramAuth:

    BASE_URL = 'https://www.instagram.com/'
    LOGIN_URL = BASE_URL + 'accounts/login/ajax/'
    USER_AGENT = 'Instagram 52.0.0.8.83 (iPhone; CPU iPhone OS 11_4 like Mac OS X; en_US; en-US; scale=2.00; 750x1334) AppleWebKit/605.1.15'
    BROWSER_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'
    CSRF_TOKEN = 'csrftoken'
    USERNAME = ''
    PASSWORD = ''

    def __init__(self):
        self.session = requests.Session()
        self.cookies = None
        self.authenticated = False
        self.logged_in = False
        self.posts = []

    def login(self):
        self.session.headers.update(
            {'Referer': self.BASE_URL, 'user-agent': self.USER_AGENT})
        response = self.session.get(self.BASE_URL)
        self.session.headers.update(
            {'X-CSRFToken': response.cookies[self.CSRF_TOKEN]})
        login_details = {'username': self.USERNAME, 'password': self.PASSWORD}
        login = self.session.post(
            self.LOGIN_URL, data=login_details, allow_redirects=True)
        self.session.headers.update(
            {'X-CSRFToken': login.cookies[self.CSRF_TOKEN]})
        self.cookies = login.cookies
        login_text = json.loads(login.text)

        if login_text.get('authenticated') and login.status_code == 200:
            self.authenticated = True
            self.logged_in = True
            self.session.headers.update(
                {'user-agent': self.BROWSER_USER_AGENT})
        else:
            print('Login failed for ' + self.USERNAME)
            if 'checkpoint_url' in login_text:
                checkpoint_url = self.BASE_URL[0:-
                                               1] + login_text['checkpoint_url']
                print('Verifying your account at ' + checkpoint_url)
                self.verify_account(checkpoint_url)

    def verify_account(self, checkpoint_url):
        self.session.headers.update({'Referer': self.BASE_URL})
        response = self.session.get(checkpoint_url)
        self.session.headers.update(
            {'X-CSRFToken': response.cookies[self.CSRF_TOKEN], 'X-Instagram-AJAX': '1'})
        self.session.headers.update({'Referer': checkpoint_url})

        mode = int(input('Choose a verification mode (0 - SMS, 1 - Email): '))
        choice_data = {'choice': mode}
        verification = self.session.post(
            checkpoint_url, data=choice_data, allow_redirects=True)
        self.session.headers.update(
            {'X-CSRFToken': verification.cookies[self.CSRF_TOKEN], 'X-Instagram-AJAX': '1'})

        code = int(input('Enter code received: '))
        code_data = {'security_code': code}
        code = self.session.post(
            checkpoint_url, data=code_data, allow_redirects=True)
        self.session.headers.update(
            {'X-CSRFToken': code.cookies[self.CSRF_TOKEN]})
        self.cookies = code.cookies
        code_text = json.loads(code.text)

        if code_text['status'] == 'ok':
            print("Successfully logged in")
            self.authenticated = True
            self.logged_in = True
        else:
            print("Failed to verify your account: " + json.dumps(code_text))


class ResultGenerator:
    def __init__(self, instagram_analyzer, users):
        self.shared_followings = instagram_analyzer.shared_followings
        self.users = users
        self.likes = instagram_analyzer.likes
        self.likes_contributors = instagram_analyzer.likes_contributors
        self.month_posts = instagram_analyzer.month_posts

    def generate_result(self):
        self._save_shared_following()
        self._save_likes_contributors_pie_chart()
        self._save_likes_bar_chart()
        self._save_monthly_posts_bar_chart()

    def _save_shared_following(self, filename='shared_following.txt', path='result'):
        with open(f'{path}/{filename}', 'w') as file:
            for following in self.shared_followings:
                file.write(f'{following}\n')

    def _save_likes_bar_chart(self, path='result'):
        y_pos = np.arange(len(self.users))
        plt.bar(self.users, self.likes.values(), align='center', alpha=0.5)
        plt.xticks(y_pos, self.users)
        plt.ylabel('Likes')
        plt.title('Total Likes Per User')
        plt.savefig(f'{path}/total_likes.png')
        plt.clf()

    def _save_likes_contributors_pie_chart(self, path='result'):
        for k, v in self.likes_contributors.items():
            labels = v.keys()
            sizes = v.values()
            fig1, ax1 = plt.subplots()
            ax1.pie(sizes, labels=labels, autopct=make_autopct(sizes),
                    shadow=True, startangle=90)
            plt.title(f'Likes Contributors for {k}')
            # Equal aspect ratio ensures that pie is drawn as a circle.
            ax1.axis('equal')
            plt.savefig(f'{path}/likes_contributor_for_{k}')
            plt.clf()

    def _save_monthly_posts_bar_chart(self, path='result'):
        for user, posts in self.month_posts.items():
            y_pos = np.arange(len(posts.items()))
            plt.bar(posts.keys(), posts.values(), align='center', alpha=0.5)
            plt.xticks(y_pos, posts.keys())
            plt.ylabel('Number of Posts')
            plt.title(f'Posts Per Month For {user}')
            plt.savefig(f'{path}/posts_per_month_for_{user}.png')
            plt.clf()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-u', '--username',
                        help='Instagram account', required=True)
    parser.add_argument('-p', '--password',
                        help='Instagram password', required=True)
    parser.add_argument('-aus', '--ausers', nargs='+', required=True,
                        help='Instagram users that needs to be analyzed')
    result = parser.parse_args()

    if (result.username or result.password) is None:
        print('Username and password must be provided in the argument')
        raise ValueError()

    instagram_analyzer = InstagramAnalyzer(result.username, result.password)
    instagram_analyzer.analyze(result.ausers, count=20)

    result_generator = ResultGenerator(instagram_analyzer, result.ausers)
    result_generator.generate_result()
