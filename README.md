# Python tools

Tools that used for work or self-interest

## [Instagram Analyzer](https://github.com/eziceice/tools/blob/master/instagram_analyzer.py)
It is a tool to analyze your instagram posts and likes with your friend, for example total likes, shared followings or likes contributors. 

**Use-age**:

    python instagram_analyzer.py -u username -p password -aus user1 user2

## [Branch Name Generator](https://github.com/eziceice/tools/blob/master/bngenerator.py)
Generate correct branch name based on requirements. 


Template: 

    investigation/<JIRA number>[ - optional description]
    bug/<JIRA number>[ - optional description]
    feature/<JIRA number>[ - optional description]
**Use-age**:

    python bngenerator.py -j 1234 -d 'this is a test'
**Output:** 

    feature/1234-this-is-a-test
