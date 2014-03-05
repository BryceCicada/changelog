#!/usr/bin/python

import sys, subprocess, getopt, re
from urllib2 import Request, urlopen, URLError, HTTPError
import xml.etree.ElementTree as ET
import ConfigParser, os
from bs4 import BeautifulSoup
from changelog.commitReader import CommitReader
from changelog.Writer import Writer



fogbugzAPI = 'https://we7.fogbugz.com/api.asp'
githubAPI = 'https://api.github.com'


fogbugz = 'https://we7.fogbugz.com/f/'
github = 'https://github.com/we7/mediagraft/commit/'

def usage(error):
    print '''Changelog
    test.py -s<commitish>|--since<commitish>

        -h  --help      This Help
        -s  --since=    Commitish to log from, Default HEAD
        -u  --until=    Commitish to log to, Default last commit
        -w  --wiki      output in wiki format

    '''
    sys.exit(error)

def readInput(argv):
    params = {'since': 'HEAD~1', 'until': '', 'wiki': False, 'all': False}
    try:
        opts, args = getopt.getopt(argv,"hwas:u:",["since=","until=","wiki","all"])
    except getopt.GetoptError:
        usage(2)
    for opt, arg in opts:
        if opt == ("-h", "--help"):
            usage(0)
        elif opt in ("-w", "--wiki"):
            params['wiki'] = True
        elif opt in ("-a", "--all"):
            params['all'] = True
        elif opt in ("-s", "--since"):
            params['since'] = arg
        elif opt in ("-u", "--until"):
            params['until'] = arg
    return params



def call(request):
    #print 'calling:' + request
    result = {}
    try:
        response = urlopen(request)
        result['body'] = response.read()
        result['code'] = response.getcode()
        #print 'got code' + str(result['code'])
    except HTTPError, e:
        result['code'] = e.getcode()
        #print 'got code' + str(result['code'])
        result['body'] = ''
    except URLError, e:
        print 'No kittez. Got an error code:', e
        exit(1)
    return result

def getCaseName(case, params):
        url = fogbugzAPI + '?cmd=search&token=' + params['token'] + '&q=' + case + '&cols=sTitle'
        result = call(url)['body']
        try:
            bugname = soup = BeautifulSoup(result, "xml").find('sTitle').text
        except AttributeError, e:
            bugname = 'NOT-FOUND'
        return bugname

def addorAppendCommit(bug, changesByBug, commit):
    commitsForBug = []
    if bug in changesByBug:
        commitsForBug = changesByBug[bug]
    commitsForBug.append(commit)
    changesByBug[bug] = commitsForBug


def ArrangeCommitsByBug(commits):
    changesByBug = {}
    for commit in commits:
        for bug in commit['closes']:

            addorAppendCommit(bug, changesByBug, commit)
        if not commit['closes']:
            addorAppendCommit('', changesByBug, commit)

    return changesByBug






def getFogbugzToken(config, params):

    url = fogbugzAPI + '?cmd=logon&email=' + config.get("fogbugz", "username") + '&password=' + config.get("fogbugz", "password")
    soup = BeautifulSoup(call(url)['body'], "xml")
    try:
        token = soup.find('token').text
    except AttributeError, e:
        print 'fogbugz login error'
        exit(0)
    return token


def main(argv):

    params = readInput(argv[1:])
    params['config'] = os.path.dirname(os.path.realpath(sys.argv[0]))+ '/config.cfg'
    config = ConfigParser.ConfigParser()
    config.readfp(open(params['config']))

    params['gitToken'] = config.get("github", "token")



    params['token'] = getFogbugzToken(config, params)

    commits = CommitReader().getCommits(params)

    fogbugzNames = {}
    for commit in commits:
        if commit['closes']:
            for caseId in commit['closes']:
                if not caseId in fogbugzNames:
                    fogbugzNames[caseId] = getCaseName(caseId, params)
        if call(githubAPI + '/repos/we7/mediagraft/git/commits/' + commit['sha'] + '?access_token=' +params['gitToken'])['code'] == 200:
            commit['onGit'] = True
            #print 'yes'
        else:
            commit['onGit'] = False
            #print 'no'

    commitsByBugNumber = ArrangeCommitsByBug(commits)

    Writer().outputData(commitsByBugNumber, fogbugzNames, params)


if __name__ == "__main__":
    main(sys.argv)