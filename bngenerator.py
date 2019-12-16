from argparse import ArgumentParser

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-c', '--category', help='branch or investigation or feature', default='feature')
    parser.add_argument('-j', '--jira', help='jira ticket number', )
    parser.add_argument('-d', '--description', help='jira ticket description')

    result = parser.parse_args()
    description = result.description.replace(' ', '-')
    ticket = f'{result.category}/{result.jira}-{description}'
    print(ticket)