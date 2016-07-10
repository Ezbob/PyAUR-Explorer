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
VERBOSE = False
ALL_PRINT = False

def argument_parse():	
	parser = argparse.ArgumentParser(description="Search for the pkg_name in the Arch User Repository")
	parser.add_argument("pkg_name", help="Package name")
	parser.add_argument("-lp","--long-print", action="store_true", help="Prints all info fields")
	parser.add_argument("-v","--verbose", action="store_true", help="Prints extra explanatory messages")
	parser.add_argument("-a","--all", action="store_true", help="If no exact match is found, print all alternatives")
	parser.add_argument("-e","--entries-shown",type=int, default=4, help="Set the maximum number of entries shown when showing alternatives. This option gets ignored if all alternatives are set to be shown")
	return parser.parse_args()

def consume_arguments():
	global VERBOSE, ALL_PRINT, ENTRIES_SHOWN, LONG_PRINT
	args = argument_parse()
	LONG_PRINT = args.long_print
	VERBOSE = args.verbose
	ALL_PRINT = args.all
	ENTRIES_SHOWN = args.entries_shown
	return args.pkg_name

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

def print_entry(entry):
	if LONG_PRINT:
		print entry['Name']
		for key, val in entry.iteritems():
			if key == 'Name':
				pass
			else:
				print "\t" + key + ": ",
				if type(val) is not str and type(val) is not unicode:
					print unicode(val)
				else:
					print val.encode('utf-8')
	else:
		if entry['Name'] != None:
			print unicode(entry['Name'])
		if entry['Description'] != None:
			print "\tDescription: " + entry['Description'].encode('utf-8')
		if entry['Maintainer'] != None:
			print "\tMaintainer: " + unicode(entry['Maintainer'])
		if entry['Version'] != None: 
			print "\tVersion: " + unicode(entry['Version'])

def show_alternatives(count, results):
	vprint("Could not find a direct match. Found " + str(count) + " alternatives:")
	if ALL_PRINT:
		for entry in results:
			print_entry(entry)
	else:
		for index in range( min( count, ENTRIES_SHOWN ) ):
			print_entry(results[index])

def vprint(message):
	if VERBOSE:
		print message

if __name__ == '__main__':
	package_name = consume_arguments()

	direct_pkg_result = None
	count, results = search_aur( package_name )
	
	if count == 0:
		vprint("No results found.")
	else:
		for result in results:
			if result['Name'] == package_name:
				direct_pkg_result = result
				results.remove(result)

		if direct_pkg_result != None:
			vprint("Found a direct match:")
			print_entry(direct_pkg_result)
		else:
			show_alternatives(count, results)
