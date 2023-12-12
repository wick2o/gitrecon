#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable-msg=C0103
# pylint: disable-msg=C0301
# pylint: disable-msg=W0611
# pylint: disable-msg=W0612
# pylint: disable-msg=W0702
# pylint: disable-msg=W0703
# pylint: disable-msg=W0621
# pylint: disable-msg=R0913
"""
Massive GitHub repo clonning
"""

import os
import sys
import datetime
import logging
import threading
import queue
import time
import urllib.request, urllib.error, urllib.parse
import coloredlogs

__author__ = "Jaime Filson <wick2o@gmail.com>, Borja Ruiz <borja@libcrack.so>"
__email__ = "wick2o@gmail.com, borja@libcrack.so"
__date__ = "Date: Wed Jan 28 16:35:57 CET 2015"
__version__ = 0.6

logname = 'gitrecon'
logfile = '{0}.log'.format(logname)

logger = logging.getLogger(logname)
#logger = logging.getLogger(__name__)

#logging.basicConfig(level=(logging.INFO))
#coloredlogs.install(level='DEBUG')                 # logs program & libs
#coloredlogs.install(level='DEBUG', logger=logger)  # logs program only
coloredlogs.install(level=logging.DEBUG, logger=logger)

# LOG_FORMAT = '%(asctime)s [%(levelname)s] %(module)s.%(funcName)s : %(message)s'

# __formatter = logging.Formatter(LOG_FORMAT)
# __streamhandler = logging.StreamHandler()
# __streamhandler.setFormatter(__formatter)
# logger.addHandler(__streamhandler)

downloaded_repos = 0
args = None
halt = False

try:
    import git
    import sqlite3
    import argparse
    import simplejson as json
except ImportError as e:
    logger.critical('Missing mandatory module(s): {0}'.format(e))
    logger.critical('Use pip install -r requirements.txt')
    sys.exit(1)


def logo():
    red1='\033[31m'
    red2='\033[91m'
    bold='\033[1m'
    reset='\033[0m'
    color1='\033[1m\033[31m'
    color2='\033[1m\033[30;41m'
    # print(red1)
    print(color2)
    print('')
    print('  __ _(_) |_ _ __ ___  ___ ___  _ __  ')
    print(' / _` | | __| \'__/ _ \/ __/ _ \| \'_ \ ')
    print('| (_| | | |_| | |  __/ (_| (_) | | | |')
    print(' \__, |_|\__|_|  \___|\___\___/|_| |_|')
    print(' |___/                                ')
    print(reset)
    print('')
    print('')
    print('Authors:')
    print('    Jaime Filson aka WiK <wick2o@gmail.com>')
    print('    Borja Ruiz <borja@libcrack.so>')
    print('License: BSD (3-Clause)\n')


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--debug', action='store_true',
                        dest='debug', default=False, help='Show debug messages')
    parser.add_argument('-m', '--method', action='store', dest='method',
                        default='https', type=str, help='Access method (git/https)')
    parser.add_argument('-r', '--repos', action='store', dest='repos',
                        default=None, type=str, help='Repo list (comma separated)')
    parser.add_argument('-t', '--threads', action='store', dest='threads',
                        default=0, type=int, help='Number of threads')
    parser.add_argument('-u', '--username', action='store', dest='username',
                        required=True, help='Github username')

    global args
    args = parser.parse_args()


def get_repo_data(user):
    url = 'https://api.github.com/users/%s/repos' % user
    req = urllib.request.Request(url)
    user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1'
    if args.debug is True:
        logger.debug('Using User-Agent %s' % user_agent)
    req.add_header('User-Agent', user_agent)
    page = urllib.request.urlopen(req)
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
    except Exception as e:
        logger.exception('There was a problem cloning %s %s' % (repo['name'], e))


def main():
    global downloaded_repos
    global args
    logo()
    parse_args()

    logfile_path = os.path.join(os.getcwd(), args.username, logfile)
    logfile_dir = os.path.dirname(logfile_path)
    if not os.path.exists(logfile_dir):
        os.mkdir(logfile_dir)

    __filehandler = logging.FileHandler(os.path.realpath(logfile_path))
    logger.addHandler(__filehandler)

    if args.debug is True:
        logger.setLevel(logging.DEBUG)

    logger.info('Using username "{0}"'.format(args.username))
    logger.info('Downloading repos from http://www.github.com/{0}'.format(args.username))

    repodata, rate_limit = get_repo_data(args.username)

    if args.repos is None:
        repos_json = json.loads(repodata)
    else:
        repos_json = ''
        tmp_list = []
        for r in args.repos.split(","):
            clone_url = None
            if args.method == "https":
                clone_url = "https://github.com/{0}/{1}.git".format(args.username, r)
            elif args.method == "git":
                clone_url = "git@github.com:{0}/{1}.git".format(args.username, r)
            else:
                logger.fatal("Unknown access method {0}".format(args.method))
                raise Exception("Unknown access method {0}".format(args.method))
            logger.info('Clone URL: {0}'.format(clone_url))
            tmp_str = {
                "clone_url": clone_url,
                "full_name": os.path.realpath("{0}/{1}".format(args.username, r)),
                "name": "{0}".format(r)}
            tmp_list.append(tmp_str)
            if args.debug is True:
                logger.debug("Adding repo: {0}".format(tmp_str))
        repos_json_dumps = json.dumps(tmp_list)
        repos_json = json.loads(repos_json_dumps)

    if args.debug is True and repos_json is not None:
        logger.debug('JSON response: {0}'.format(repos_json))

    if args.threads > 1:
        q = queue.Queue()
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

    if args.debug is True:
        logger.debug('Creating a database in memory')

    db = sqlite3.connect(':memory:')
    cur = db.cursor()
    cur.execute('CREATE TABLE files (id INTEGER PRIMARY KEY, name \
                varchar(255) UNIQUE, count int DEFAULT 1)')
    cur.execute('CREATE TABLE dirs (id INTEGER PRIMARY KEY, name \
                varchar(255) UNIQUE, count int DEFAULT 1)')

    if args.debug is True:
        logger.debug('Populating the database')

    for root, dirs, files in os.walk('./%s' % args.username):
        for m_file in files:
            try:
                cur.execute('INSERT INTO files (name) VALUES (?)',
                            (os.path.join(root, m_file),))
            except sqlite3.IntegrityError:
                cur.execute('UPDATE files SET count = count + 1 WHERE \
                name = ?', (os.path.join(root, m_file)))
        for m_dir in dirs:
            try:
                cur.execute('INSERT INTO dirs (name) VALUES (?)',
                            (os.path.join(root, m_dir),))
            except sqlite3.IntegrityError:
                cur.execute('UPDATE dirs SET count = count + 1 \
                           WHERE name = ?' % (os.path.join(root, m_dir)))

    if args.debug is True:
        logger.debug('Generating the files wordlist')

    try:
        cur.execute('SELECT name FROM files ORDER BY count DESC')
        res = cur.fetchall()
    except sqlite3.OperationalError as e:
        logger.exception('Error getting file list from database: {0}'.format(e))

    filename = '%s/%s-files.txt' % (args.username, args.username)
    logger.info('Writing %s' % filename)
    try:
        fp = open(filename, 'w')
        for itm in res:
            encoded_itm = itm[0].encode('utf8')
            if isinstance(itm[0], str):
                encoded_itm = itm[0].encode('utf8')
            else:
                encoded_itm = str(itm[0]).encode('utf8')
            fp.write('%s\n' % (encoded_itm))
        fp.close()
    except (OSError, IOError) as e:
        logger.exception('Cannot write to "{0}": {1}'.format(filename, e))

    if args.debug is True:
        logger.debug('Generating the dirs wordlist')

    cur.execute('SELECT name FROM dirs ORDER BY count DESC')
    res = cur.fetchall()

    filename = '%s/%s-dirs.txt' % (args.username, args.username)
    logger.info('Writing %s' % filename)
    try:
        fp = open(filename, 'w')
        for itm in res:
            fp.write('%s\n' % (itm[0]))
        fp.close()
    except (OSError, IOError) as e:
        logger.exception('Cannot write to "{0}": {1}'.format(filename,e))

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

# vim:ts=4 sts=4 tw=100:
