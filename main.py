#!/usr/bin/python2
import requests
import os
import shutil
import tempfile
import argparse

AUR_URL = "https://aur.archlinux.org"
RPC_URL = AUR_URL + "/rpc"

ENTRIES_SHOWN = 4
LONG_PRINT = False

def argument_parse():	
	parser = argparse.ArgumentParser(description="Get stuff from the Arch User Repository")
	parser.add_argument("pkg_name", help="Package name")
	parser.add_argument("-lp","--long-print", help="Print all info fields")
	return parser.parse_args()

def open_get_request(url, params):
	req = requests.get( url, params=params )
	req.raise_for_status()
	return req

def check_json(req):
	if req.headers['Content-Type'] == "application/json":
		return req.json()
	return req 

def search_aur( pkg_name ):
	params = { 'v' : '5' }
	params['type'] = 'search'
	params['arg'] = pkg_name
	json = check_json( open_get_request( RPC_URL, params ) )
	return json['resultcount'], json['results']

def print_entry(entry, long_version=False):
	if long_version:
		print entry['Name']
		for key, val in entry.iteritems():
			if key == 'Name':
				pass
			else:
				print "\t" + key + ": " + str(val)
	else:
		if entry['Name'] != None:
			print entry['Name']
		if entry['Description'] != None:
			print "\t\"" + entry['Description'] + "\""
		if entry['Maintainer'] != None:
			print "\tMaintainer: " + entry['Maintainer']
		if entry['Version'] != None: 
			print "\tVersion: " + entry['Version']

if __name__ == '__main__':
	args = argument_parse()

	direct_pkg_result = None
	count, results = search_aur( args.pkg_name )
	
	if count == 0:
		print "No results found."
	else:
		for result in results:
			if result['Name'] == args.pkg_name:
				direct_pkg_result = result
				results.remove(result)

		#print results[0].keys()

		if direct_pkg_result != None:
			print "Found a direct match:"
			print_entry(direct_pkg_result)
		else:
			print "Could not find a direct match. Found alternatives:"
			for index in range( min( count, ENTRIES_SHOWN ) ):
				print_entry(results[index], True)

#	dirpath = tempfile.mkdtemp()
#	os.chdir( dirpath )

#	shutil.rmtree( dirpath )
	