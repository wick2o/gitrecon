#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import datetime
import threading
import Queue
import time
import urllib2

if sys.version[0] == '3':
    raise Exception('Python3 is not supported')

MYPATH = os.path.abspath(os.path.expanduser(__file__))
if os.path.islink(MYPATH):MYPATH = os.readlink(MYPATH)
MYLIBPATH = os.path.dirname(MYPATH) + '/lib/'
sys.path.append(os.path.dirname(MYLIBPATH))

import Colors
from Logger import Logger

logger = Logger.logger
colors = Colors.Colors()

logfile = 'gitrecon.log'

downloaded_repos = 0
args = None
halt = False

try:
    import argparse
except ImportError as e:
    logger.error('Missing needed module: easy_install argparse')
    halt = True

try:
    import git
except ImportError as e:
    logger.error('Missing needed module: easy_install gitpython')
    halt = True

try:
    import simplejson as json
except ImportError as e:
    logger.error('Missing needed module: easy_install simplejson')
    halt = True

try:
    import sqlite3
except ImportError as e:
    logger.error('Missing needed module: easy_install sqlite3')
    halt = True

if halt:
    sys.exit(1)


def logo():
    print('%s       _ _                            ' % (colors.red))
    print('  __ _(_) |_ _ __ ___  ___ ___  _ __  ')
    print(' / _` | | __| \'__/ _ \/ __/ _ \| \'_ \ ')
    print('| (_| | | |_| | |  __/ (_| (_) | | | |')
    print(' \__, |_|\__|_|  \___|\___\___/|_| |_|')
    print(' |___/                                ')
    print('%s' % colors.reset)
    print('Authors:')
    print('    Jaime Filson aka WiK <wick2o@gmail.com>')
    print('    Borja Ruiz <borja@libcrack.so>')
    print('License: BSD (3-Clause)\n')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', action='store', dest='username', required=True, help='Github Username')
    parser.add_argument('-t', '--threads', action='store', dest='threads', default=0, type=int, help='Number of threads')
    parser.add_argument('-d', '--debug', action='store_true', dest='debug', help='Show debug messages')
    global args
    args = parser.parse_args()


def get_repo_data(user):
    url = 'https://api.github.com/users/%s/repos' % user
    req = urllib2.Request(url)
    user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1'
    logger.debug('Using User-Agent %s' % user_agent)
    req.add_header('User-Agent',user_agent)
    page = urllib2.urlopen(req)
    page_content = page.read()
    page.close()
    return page_content, page.info()['X-RateLimit-Remaining']


def dl_worker(repo):
    global downloaded_repos
    try:
        logger.info('Cloning %s' % repo['clone_url'])
        dlw_res = git.Git().clone(repo['clone_url'], repo['full_name'])
        downloaded_repos = downloaded_repos + 1
        logger.info('Completed %s' % repo['name'])
        del dlw_res
    except Exception as err:
        logger.error('There was a problem cloning %s %s' % (repo['name'], err.message))


def main():
    global downloaded_repos
    global args
    logo()
    parse_args()
    repos, rate_limit = get_repo_data(args.username)
    repos_json = json.loads(repos)

    logfile_path = os.path.join(os.getcwd(),args.username,logfile)
    Logger.add_file_handler(logfile_path)

    logger.info('Using username %s' % args.username)
    logger.info('Downloading repos from http://www.github.com/%s' % args.username)

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

    logger.info('You may request up to %s more users this hour' % rate_limit)

    logger.info('Generating wordlists')

    if args.debug:
        logger.debug('Creating a database in memory')

    db = sqlite3.connect(':memory:')
    cur = db.cursor()
    cur.execute('CREATE TABLE files (id INTEGER PRIMARY KEY, name \
                varchar(255) UNIQUE, count int DEFAULT 1)')
    cur.execute('CREATE TABLE dirs (id INTEGER PRIMARY KEY, name \
                varchar(255) UNIQUE, count int DEFAULT 1)')

    if args.debug:
        logger.debug('Populating the database')

    for root, dirs, files in os.walk('./%s' % args.username):
        for m_file in files:
            try:
                cur.execute('INSERT INTO files (name) VALUES (?)',
                        (os.path.join(root,m_file),))
            except sqlite3.IntegrityError:
                cur.execute('UPDATE files SET count = count + 1 WHERE \
                name = ?', (os.path.join(root,m_file)))
        for m_dir in dirs:
            try:
                cur.execute('INSERT INTO dirs (name) VALUES (?)',
                        (os.path.join(root,m_dir),))
            except sqlite3.IntegrityError:
                cur.execute('UPDATE dirs SET count = count + 1 \
                           WHERE name = ?' % (os.path.join(root, m_dir)))

    if args.debug:
        logger.debug('Generating the files wordlist')

    try:
        cur.execute('SELECT name FROM files ORDER BY count DESC')
        res = cur.fetchall()
    except sqlite3.OperationalError as e:
        logger.error('Error getting file list from database')

    filename = '%s/%s-files.txt' % (args.username,args.username)
    logger.info('Writing %s' % filename)
    try:
        fp = open(filename, 'w')
        for itm in res:
            encoded_itm = itm[0].encode('utf8')
            if isinstance(itm[0],basestring):
                encoded_itm = itm[0].encode('utf8')
            else:
                encoded_itm = unicode(itm[0]).encode('utf8')
            fp.write('%s\n' % (encoded_itm))
        fp.close()
    except (OSError, IOError):
        logger.error('Cannot write to %s' % filename)

    if args.debug:
        logger.debug('Generating the dirs wordlist')

    cur.execute('SELECT name FROM dirs ORDER BY count DESC')
    res = cur.fetchall()

    filename = '%s/%s-dirs.txt' % (args.username,args.username)
    logger.info('Writing %s' % filename)
    try:
        fp = open(filename, 'w')
        for itm in res:
            fp.write('%s\n' % (itm[0]))
        fp.close()
    except (OSError, IOError):
        logger.error('Cannot write to %s' % filename)

    if cur:
        cur.close()
        del cur
    if db:
        db.close()
        del db

    logger.info('Cloned %s repos from http://www.github.com/%s' % (downloaded_repos,args.username))
    logger.info('Logfile saved %s' % logfile_path)

if __name__ == '__main__':
    main()
