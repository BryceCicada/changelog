__author__ = 'arthur'

import re
import subprocess

class CommitReader:

    def __init__(self):
        self.closesPattern = re.compile(r"(?:closes(?::)?\s*(?:#)?([0-9]*))", re.IGNORECASE)
        self.changelogPattern = re.compile(r"changelog", re.IGNORECASE)
        self.commitPattern = re.compile(r"\s*(?:commit)?\s*(?P<Sha>[\w]{40})\n(?:Merge: (?P<Merge>([\w]*) ([\w]*))\n)?Author: (?P<Author>.*) <(?P<Email>[\w\-@.]*)>\nDate:\s*(?P<Date>[a-zA-Z\s]* [0-9:\s]* \+[0-9]{4})\n(?P<Body>.*)", re.DOTALL)
        self.testPattern = re.compile(r".*test.*", re.IGNORECASE|re.DOTALL)
        self.ignorePattern = re.compile(r"(?:ignore)", re.IGNORECASE)






    def processCommit(self, commit):
        result = self.commitPattern.match(commit)
        parts = {}

        if result:
            parts['sha'] = result.group(1)
            parts['author'] = result.group(5)
            parts['body'] = result.group(8)
            parts['merge'] = result.group(2)
            parts['ignore'] = self.ignorePattern.findall(parts['body'])

            testsResult = self.testPattern.match(parts['body'])
            if testsResult:
                bodyParts = re.split(r'test(?:s)?(?::)?', parts['body'], 1, re.IGNORECASE)
                parts['test'] = bodyParts[1]
                parts['strippedBody'] = bodyParts[0]
            else:
                parts['strippedBody'] = parts['body']

            parts['strippedBody'] = re.sub(self.closesPattern, '', parts['strippedBody'])
            parts['strippedBody'] = parts['strippedBody'].strip()

            parts['closes'] = self.closesPattern.findall(parts['body'])
            parts['changelog'] = self.changelogPattern.findall(parts['body'])

        else:
            print 'Unexpected Commit format!\n', commit
            exit(1)

        return parts

    def getCommits(self, params):
        command = ["git", "log", params['since'] + '..']
        output = subprocess.check_output(command)
        split = str(output).split('\ncommit ')
        commits = []

        for commitString in split:
            commit = self.processCommit(commitString)
            if (commit['changelog'] or params['all'] is True) and bool(commit['merge']) is False and bool(commit['ignore']) is False:
                commits.append(commit)
        return commits