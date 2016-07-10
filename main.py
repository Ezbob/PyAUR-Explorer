#!/usr/bin/python2
import requests
import os
import shutil
import tempfile
import argparse

aur_url = "https://aur.archlinux.org"
rpc_url = aur_url + "/rpc"

def argument_parse():	
	parser = argparse.ArgumentParser(description="Get stuff from the Arch User Repository")
	parser.add_argument("pkg_name", help="Package name")
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
	json = check_json( open_get_request( rpc_url, params ) )
	return json['resultcount'], json['results']


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

		if direct_pkg_result != None:
			print "Found a direct match."
		else:
			print "Could not find a direct result. Found alternatives:"
			for index in range( min( count, 3 ) ):
				print results[index]['Name'] 

#	dirpath = tempfile.mkdtemp()
#	os.chdir( dirpath )

#	shutil.rmtree( dirpath )
	