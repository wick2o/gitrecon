#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import datetime
import threading
import Queue
import time
import urllib2

halt = False

try:
    import argparse
except ImportError as e:
    print 'Missing needed module: easy_install argparse'
    halt = True

try:
    import git
except ImportError as e:
    print 'Missing needed module: easy_install gitpython'
    halt = True

try:
    import simplejson as json
except ImportError as e:
    print 'Missing needed module: easy_install simplejson'
    halt = True

try:
    import sqlite3
except ImportError as e:
    print 'Missing needed module: easy_install sqlite3'
    halt = True

if halt:
    sys.exit()


def logo():
    print "       _ _                            "
    print "  __ _(_) |_ _ __ ___  ___ ___  _ __  "
    print " / _` | | __| '__/ _ \/ __/ _ \| '_ \ "
    print "| (_| | | |_| | |  __/ (_| (_) | | | |"
    print " \__, |_|\__|_|  \___|\___\___/|_| |_|"
    print " |___/                                "
    print "Author: Jaime Filson aka WiK"
    print "Email: wick2o@gmail.com"
    print "License: BSD (3-Clause)"
    print ""


def setup():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', action='store', dest='username', required=True, help='Github Username')
    parser.add_argument('-t', '--threads', action='store', dest='threads', default=0, type=int,
                        help='Enable Threading. Specify max # of threads')
    parser.add_argument('-d', '--debug', action='store_true', dest='debug', help='Show debug messages')
    global args
    args = parser.parse_args()


def get_repo_data(user):
    url = 'https://api.github.com/users/%s/repos' % user
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.3; \
        WOW64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1')
    page = urllib2.urlopen(req)
    page_content = page.read()
    page.close()
    return page_content, page.info()['X-RateLimit-Remaining']


def dl_worker(repo):
    try:
        print '%s Cloning %s' % (datetime.datetime.now(), repo['name'])

        dlw_res = git.Git().clone(repo['clone_url'], repo['full_name'])

        print '%s Completed %s' % (datetime.datetime.now(), repo['name'])
        del dlw_res
    except Exception as err:
        print '%s There was a problem cloning %s %s' % (datetime.datetime.now(), repo['name'], err.message)


def main():
    logo()
    setup()

    repos, rate_limit = get_repo_data(args.username)
    repos_json = json.loads(repos)

    if args.threads > 1:
        q = Queue.Queue()
        threads = []
        for itm in repos_json:
            q.put(itm)
        while not q.empty():
            if args.threads >= threading.activeCount():
                q_itm = q.get()
                try:
                    t = threading.Thread(target=dl_worker, args=(q_itm,))
                    t.daemon = True
                    t.start()
                finally:
                    q.task_done()
        while threading.activeCount() > 1:
            time.sleep(0.1)
        for thread in threads:
            thread.join()
        q.join()
    else:
        for itm in repos_json:
            dl_worker(itm)

    print '%s You may request up to %s more users this hour' % \
        (datetime.datetime.now(), rate_limit)
    print '%s Generating wordlists' % \
        (datetime.datetime.now())

    if args.debug:
        print '%s [DEBUG] Creating a database in memory' % \
            (datetime.datetime.now())
    db = sqlite3.connect(":memory:")
    cur = db.cursor()
    cur.execute('CREATE TABLE files (id INTEGER PRIMARY KEY, name \
                varchar(255) UNIQUE, count int DEFAULT 1)')
    cur.execute('CREATE TABLE dirs (id INTEGER PRIMARY KEY, name \
                varchar(255) UNIQUE, count int DEFAULT 1)')

    if args.debug:
        print '%s [DEBUG] Populating the database' % (datetime.datetime.now())

    for r, d, f in os.walk('./%s' % args.username):
        for m_file in f:
            try:
                cur.execute("INSERT INTO files ('name') VALUES ('%s')" % m_file)
            except sqlite3.IntegrityError:
                cur.execute("UPDATE files SET count = count + 1 WHERE \
                name = '%s'" % m_file)
        for m_dir in d:
            try:
                cur.execute("INSERT INTO dirs ('name') VALUES ('%s')" % m_dir)
            except sqlite3.IntegrityError:
                cur.execute("UPDATE dirs SET count = count + 1 \
                           WHERE name = '%s'" % m_dir)

    if args.debug:
        print '%s [DEBUG] Generating the files wordlist' % \
            (datetime.datetime.now())

    cur.execute("SELECT name FROM files ORDER BY count DESC")
    res = cur.fetchall()
    fp = open('./%s-files.txt' % args.username, 'w')

    for itm in res:
        fp.write('%s\n' % (itm[0]))
    fp.close()

    if args.debug:
        print '%s [DEBUG] Generating the dirs wordlist' % \
            (datetime.datetime.now())

    cur.execute("SELECT name FROM dirs ORDER BY count DESC")
    res = cur.fetchall()
    fp = open('./%s-dirs.txt' % args.username, 'w')

    for itm in res:
        fp.write('%s\n' % (itm[0]))
    fp.close()

    if cur:
        cur.close()
        del cur
    if db:
        db.close()
        del db

if __name__ == '__main__':
    main()
