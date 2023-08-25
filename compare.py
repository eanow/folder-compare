#!/usr/bin/python3
import hashlib
import os
import argparse


def generate_folder_hash(folder):
    reference=list()
    for root,dirs,files in os.walk(folder):
        for name in files:
            full_path=os.path.join(root,name)
            with open(full_path,"rb") as f:
                sha256_hash=hashlib.sha256()
                for block in iter(lambda: f.read(4096),b""):
                    sha256_hash.update(block)
                entry=full_path.replace(folder,"")+"|"+sha256_hash.hexdigest()
                reference.append(entry)
    return reference
def compare_sets(reference_a,reference_b,ref_a_name,ref_b_name,verbose):
    #count each set
    count_a=len(reference_a)
    count_b=len(reference_b)
    #create orphaned lists
    a_missing=set(reference_a)-set(reference_b)
    b_missing=set(reference_b)-set(reference_a)
    missing_count_a=len(a_missing)
    missing_count_b=len(b_missing)
    print("Total Number of files in "+ref_a_name+" (A): "+str(count_a))
    print("Total Number of files in "+ref_b_name+" (B): "+str(count_b))
    print("Number of files seen in A but not B: " + str(missing_count_a))
    print("Number of files seen in B but not A: " + str(missing_count_b))


#usage:
#compare folderA folderB
#generates a list of the files in each folder and hashes them, and reports 
#total number of files in A, B
#number of files in A that differ from B
#number of files in B that differ from A
#--list-all prints out the different files
#--create-reference [file] will output a text file to [file] that lists files and hashes for folder A
#--use-reference [file] will use a text file in place of folder B

parser=argparse.ArgumentParser(prog='Folder Compare',
                        description='Utility for comparing two directory trees, generally expected to be similar')
parser.add_argument('folderA', help='First folder to compare')
parser.add_argument('folderB', nargs='?', help='Second folder to compare. Omit if using -c or -u options.')

parser.add_argument('-c', '--create-reference', metavar='Reference Output File', 
            help='File to write comparison information to. Will scan first folder and produce a reference file for later use with the --use-reference option.')
parser.add_argument('-u', '--use-reference', metavar='Reference Input File', 
            help='File to read comparison information to. Will use this comparison information in place of folderB.')
parser.add_argument('-l', '--list-all', action='store_true')

args=parser.parse_args()

#regardless, we will be generating a reference set for folder A
print("Walking folder "+args.folderA+" and computing a hash of each file.")
reference_a=generate_folder_hash(args.folderA)
#if we're in create reference mode, write out and quit
if args.create_reference is not None:
    outfile=open(args.create_reference,"w")
    outfile.write('\n'.join(reference_a))
    print('Reference File written to ' + args.create_reference)
    quit()
#get reference set b
if args.folderB is not None:
    reference_b=generate_folder_hash(args.folderB)
    compare_sets(reference_a,reference_b,args.folderA,args.folderB,args.list_all)
elif args.use_reference is not None:
    reference_b=open(args.use_reference).read().splitlines()
    compare_sets(reference_a,reference_b,args.folderA,args.use_reference,args.list_all)
else:
    #something bad happened
    print("Second reference set not available; check arguments.")
    quit()


    