__author__ = 'arthur'

class Writer:
    def __init__(self):
        pass

    def commitBodySection(self, commit, params):
        if params['wiki']:
            if not 'onGit' in commit:
                print str(commit)
            if commit['onGit']:
                print("\t\t\t* [[" + params['gitRepoUrl'] + commit['sha'] + '|[' + commit['sha'][:5] + ']]] ' + commit['author']),
            else:
                print("\t\t\t* " + commit['sha'] + ' ' + commit['author']),
            if commit['strippedBody']:
                print '<WRAP  prewrap><code>' + commit['strippedBody'] + '</code></WRAP>'
            else:
                print ''
        else:
            print("\t\t\t* [" + commit['sha'] + '] ' + commit['author']),
            if commit['strippedBody']:
                print commit['strippedBody']
            else:
                print ''

    def testSection(self, commit, params):
        if 'test' in commit:
            if params['wiki']:
                if commit['onGit']:
                    print("\t\t\t* [[" + params['gitRepoUrl'] + commit['sha'] + '|[' + commit['sha'][:5] + ']]] ' + commit['author']),
                else:
                    print("\t\t\t* " + commit['sha'] + ' ' + commit['author']),
                print '<WRAP  prewrap><code>' + commit['test'] + '</code></WRAP>'
            else:
                print "\t\t\t* [" + commit['sha'] + '] ' + commit['author']
                print commit['test'].strip()

    def printBugSection(self, bugNumber, params, commits):
        if params['wiki']:
            print '=== Commits ==='
        else:
            print 'Commits:'

        for commit in commits:
            self.commitBodySection(commit, params)

        printTest = False
        for commit in commits:
            if 'test' in commit:
                printTest = True

        if printTest:
            if params['wiki']:
                print '=== Tests ==='
            else:
                print 'Tests:'
            for commit in commits:
                self.testSection(commit, params)
        print ''

    def printOtherSection(self, bugNumber, params, commits):
        for commit in commits:
            self.commitBodySection(commit, params)
            if 'test' in commit:
                if params['wiki']:
                    print '=== Test ==='
                else:
                    print 'Test:'
                self.testSection(commit, params)
        print ''


    def outputData(self, changesByCase, fogbugzNames, params):
        if params['wiki'] and len(changesByCase) > 0:
            print '======= Resolved Bugz ======='
            for caseId in changesByCase.keys():
                if caseId and fogbugzNames[caseId] != 'NOT-FOUND':
                    print "\t* " + '[[#' + caseId + ' ' + fogbugzNames[caseId] + ']]'

        for caseId, commit in changesByCase.iteritems():
            if caseId == '':
                continue

            if params['wiki']:
                if fogbugzNames[caseId] != 'NOT-FOUND':
                    print "======" + caseId + ' ' + fogbugzNames[caseId] + '======'
                    print "Fogbugz case: " + '[[https://we7.fogbugz.com/f/cases/' + caseId + '|' + caseId + ' ' + fogbugzNames[caseId] + ']]'
                else:
                    print "======" + caseId + ' ' + fogbugzNames[caseId] + '======'
            else:
                print  caseId + " " + fogbugzNames[caseId]

            self.printBugSection(caseId, params, commit)

        if '' in changesByCase:
            if params['wiki']:
                print '====== Other Changes ======'
            else:
                print 'Other Changes'
            self.printOtherSection('', params, changesByCase[''])