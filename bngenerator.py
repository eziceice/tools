from argparse import ArgumentParser

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-c', '--category', help='bug or investigation or feature', default='feature')
    parser.add_argument('-j', '--jira', help='jira ticket number', )
    parser.add_argument('-d', '--description', help='jira ticket description')

    result = parser.parse_args()
    description = result.description.replace(' ', '-')
    ticket = f'{result.category}/{result.jira}-{description}'
    print(ticket)

'''
investigation/<JIRA number>[ - optional description]
bug/<JIRA number>[ - optional description]
feature/<JIRA number>[ - optional description]
'''

test