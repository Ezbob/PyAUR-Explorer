#!/usr/bin/python
import requests
import os
import shutil
import tempfile
import argparse
import sys
import tarfile
import subprocess

AUR_URL = "https://aur.archlinux.org"
RPC_URL = AUR_URL + "/rpc"

OPTIONS = {}

def argument_parse():   
    parser = argparse.ArgumentParser(
        description="Search for the pkg_name in the Arch User Repository")
    parser.add_argument("pkg_name", 
        help="Package name")
    parser.add_argument("-lp","--long-print", action="store_true", 
        help="Prints all info fields")
    parser.add_argument("-v","--verbose", action="store_true", 
        help="Prints extra explanatory messages")
    parser.add_argument("-a","--all", action="store_true", 
        help="If no exact match is found, print all alternatives")
    parser.add_argument("-e","--entries-shown",type=int, default=4, 
        help="Set the maximum number of entries shown when showing alternatives. This option gets ignored if all alternatives are set to be shown")
    parser.add_argument("-d","--download", action="store_true", 
        help="Download the package if a exact match was found")
    parser.add_argument("-o","--output",default="packages/", 
        help="Set the output directory for downloading packages. Default: packages/")
    parser.add_argument("-i","--install",action="store_true", 
        help="Download and install the package using makepkg")
    return parser.parse_args()

def consume_arguments():
    global OPTIONS
    args = argument_parse()
    OPTIONS['LONG_PRINT'] = args.long_print
    OPTIONS['VERBOSE'] = args.verbose
    OPTIONS['ALL_PRINT'] = args.all
    OPTIONS['ENTRIES_SHOWN'] = args.entries_shown
    OPTIONS['DOWNLOAD'] = args.download
    OPTIONS['OUT_DIR'] = args.output
    OPTIONS['INSTALL'] = args.install
    return args.pkg_name

def open_get_request(url, params, stream=False):
    req = requests.get( url, params=params, stream=stream )
    req.raise_for_status()
    return req

def check_json(req):
    if req.headers['Content-Type'] == "application/json":
        return req.json()
    return req 

# valid types are 'search' and 'info'
def get_json_from_aur(pkg_name, request_type='search'):
    params = { 'v' : '5' }
    params['type'] = request_type
    params['arg'] = pkg_name
    json = check_json( open_get_request( RPC_URL, params ) )
    return json['resultcount'], json['results']

def ask( message ):
    if sys.version_info[0] == 2:
        return raw_input(message)
    else:
    	return input(message)

def decode(message, encoding='utf-8'):
	if type(message) == bytes:
		return message.decode(encoding)
	return message

def print_entry(entry):
    if OPTIONS['LONG_PRINT']:
        print( decode(entry['Name']) )
        for key, val in entry.items():
            if key == 'Name':
                pass
            else:
                print( "\t{}: {}".format(key, decode(val)) )
    else:
        keys = ['Description', 'Maintainer', 'Version', 'Popularity']
        if entry['Name'] != None:
            print( decode(entry['Name']) )
        for key in keys:
            print( "\t{}: {}".format(key, decode( entry[key])))

def show_alternatives(count, results):
    vprint("Could not find a direct match. Found {} alternatives:".format(count))
    if OPTIONS['ALL_PRINT']:
        for entry in results:
            print_entry(entry)
    else:
        step = OPTIONS['ENTRIES_SHOWN']

        next_index = min( count, step )
        do_loop = True
        index = 0
        while do_loop:
            for index in range( index, next_index ):
                print_entry( results[index] )

            index += 1
            diff = count - index 
            
            if diff - 1 < step:
                next_index = count
            else:
                next_index += step
        
            if diff == 0:
                choice_msg = "No more entries. Press Enter to exit."
            else:
                choice_msg = "Press Enter to show the next {} entries or q to quit: ".format(diff)

            choice = ask(choice_msg).strip().lower()

            if diff == 0 or choice == "q":
                do_loop = False
                
def vprint(message):
    if OPTIONS['VERBOSE']:
        print(message)

def add_trailing_slash( path ):
    return path if path.endswith("/") else path + "/"

def download_package(filename, tar_url, chunk_size=64):
    download_url = AUR_URL + tar_url

    if not os.path.exists(OPTIONS['OUT_DIR']):
        os.mkdir(OPTIONS['OUT_DIR'])
    elif not os.path.isdir(OPTIONS['OUT_DIR']):
        print("Output directory chosen is not a directory. Exiting.")
        return

    path_to = add_trailing_slash( OPTIONS['OUT_DIR'] )

    file_path = path_to + filename
    download_request = open_get_request( download_url, params={}, stream=True )

    with open(file_path, 'wb') as file:
        for chunk in download_request.iter_content(chunk_size):
            file.write(chunk)
    return file_path

def find_pkgbuild_file(path):
    for file in os.listdir(path):
        if file == "PKGBUILD":
            return True
    return False

def install_package(file_path):
    temp_dir = tempfile.mkdtemp()
    shutil.copy(file_path, temp_dir)

    tar_filename = file_path.split("/")[-1]
    temp_path = add_trailing_slash(temp_dir) + tar_filename 
    tar_file = tarfile.open(temp_path) 

    print("Package contains the following entries:")
    tar_file.list()

    choice = ask("\nProceed with extraction? [N,y] ").strip().lower()
    if choice == "y":
        vprint("Extracting...")
        tar_file.extractall( path=temp_dir )
        vprint("Extracted.")

        extracted_dir = add_trailing_slash(temp_dir) + tar_filename.split(".")[0]

        vprint("Installing using makepkg")
        os.chdir(extracted_dir)

        vprint("Searching for PKGBUILD file...")
        if not find_pkgbuild_file( extracted_dir ):
            print("Error: could not find PKGBUILD exiting...")
  
        vprint("PKGBUILD found.")

        vprint("Parsing control to makepkg.")
        exitcode = subprocess.call(['makepkg', "-sir"])
        
        if exitcode == 0:
            vprint("Installation was successful!")
        else:
            vprint("Installation was unsuccessful.")

    if os.path.exists( temp_dir ):
        shutil.rmtree( temp_dir )

def direct_match( match_pkg ):
    vprint("Found a direct match:")
    print_entry(match_pkg)
    filename = match_pkg['URLPath'].split('/')[-1] 
    if OPTIONS['INSTALL']:
        print( "WARNING: Packages can contain malicious code. Install only from trusted sources." )
        choice = ask("Install package {} anyway? [N,y] ".format( match_pkg['Name'] ))
        if choice.strip().lower() == "y":
            vprint("Downloading...")
            file_path = download_package(filename, match_pkg['URLPath'])
            vprint("Downloaded. Saved as {}".format( file_path ))
            install_package( file_path )

    elif OPTIONS['DOWNLOAD']:
        choice = ask("Download {}? [N,y] ".format(filename))
        if choice.strip().lower() == "y":
            vprint("Downloading...")
            file_path = download_package(filename, match_pkg['URLPath'])
            vprint("Downloaded. Saved as {}".format(file_path))

def find_direct_match( results ):
    direct_pkg_result = None
    for result in results:
            if result['Name'] == package_name:
                direct_pkg_result = result
                results.remove(result)
    return direct_pkg_result

if __name__ == '__main__':
    package_name = consume_arguments()

    direct_pkg_result = None
    count, results = get_json_from_aur( package_name )
    
    if count == 0:
        vprint("No results found.")
    else:
        direct_pkg_result = find_direct_match(results)

        results = sorted(results, 
            key=lambda entry: entry['Popularity'], reverse=True) 

        if direct_pkg_result != None:
            direct_match( direct_pkg_result )
        else:
            show_alternatives( count, results )

