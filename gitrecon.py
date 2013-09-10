#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import datetime
import threading
import Queue
import time
import signal
import urllib
import urllib2

halt = False

try:
	import argparse
except ImportError:
	print 'Missing needed module: easy_install argparse'
	halt = True

try:
	import git
except ImportError:
	print 'Missing needed module: easy_install gitpython'
	halt = True
	
try:
	import simplejson as json
except ImportError:
	print 'Missing needed module: easy_install simplejson'
	halt = True
	
if halt == True:
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
	parser.add_argument('-t', '--threads', action='store', dest='threads', default=0, type=int, help='Enable Threading. Specifiy max # of threads')
	parser.add_argument('-d', '--debug', action='store_true', dest='debug', help='Show debug messages')
	
	global args
	args = parser.parse_args()
	
def get_repo_data(user):
	url = 'https://api.github.com/users/%s/repos' % (user)
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1')
	
	page = urllib2.urlopen(req)
	page_content = page.read()
	page.close()
	
	return page_content, page.info()['X-RateLimit-Remaining']

def dl_worker(repo):
	try:
		print '%s Cloning %s' % (datetime.datetime.now(), repo['name'])
		dlw_res = git.Git().clone(repo['clone_url'], repo['full_name'])
		print '%s Completed %s' % (datetime.datetime.now(), repo['name'] )
		del dlw_res
	except:
		print '%s There was a problem cloning %s' (datetime.datetime.now(), repo['name'])

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
			
	print 'You may request up to %s more users this hour' % (rate_limit)

if __name__ == '__main__':
	main()


