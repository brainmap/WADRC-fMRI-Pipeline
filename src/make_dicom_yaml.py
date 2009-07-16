#!/usr/bin/env python

import os, sys
import sqlite3, yaml
import subprocess
import optparse

DBPATH = "/Data/home/kris/TextMateProjects/TransferScans/db/development.sqlite3"
DB = sqlite3.connect(DBPATH)
CURSOR = DB.cursor()

class YamlProcessor:

	# Required entires for a self.YAML files where recon_type = 'anat'
	ANAT_YAML_ENTRIES = set(["output_dir", "prefix", "modality", "anat_type", "input_dir", "dcmglob"])
	# Required entires for a self.YAML files where recon_type = 'fmri'
	FMRI_YAML_ENTRIES = set(["output_dir", "prefix", "bold_reps", "repetition_time", "input_dir", "slices", "dcmglob"])
	# Process a complete scan directory, i.e. one containing subdirectories that
	# contain dicoms.


	#scan_dir is the scan directory for a visit, i.e. it should contain subfolders which in
	# turn contain dicoms.
	def __init__(self, visit_dir):
		self.visit_dir = visit_dir
		#Keep FSL from rezipping the output of avwroi.
		os.environ['FSLOUTPUTTYPE']="NIFTI"

	####################################################################
	## Methods to do with building yaml files.
	####################################################################

	# Create the yaml files for a visit directory.
	def create_yaml_files(self, options):
		# Find the id of the given visit.
		print 'SELECT id FROM visits WHERE path=%s' % (self.visit_dir,)
		CURSOR.execute('SELECT id FROM visits WHERE path=?', (self.visit_dir,))
		visit_id = CURSOR.fetchall()[0][0]
		# Find the details for all of the scans associated with that visit.
		CURSOR.execute("SELECT series_description, path, glob, bold_reps, slices_per_volume FROM image_datasets WHERE visit_id=?", (visit_id,))
		# Go through the scans and create the yaml files.
		for series_description, path, glob, bold_reps, slices_per_volume in list(CURSOR):
			short_description, anat_type = self.get_series_details(series_description)

			# Get a hash table that will be dumped as the yaml file.
			yaml_hash = self.make_yaml_hash(
				series_description=series_description,
				anat_type=anat_type,
				scan_path = str(path),
				glob=str(glob),
				short_description = short_description,
				prefix = options.prefix,
				output_dir = options.output_dir,
				output_file = options.output_file,
				bold_reps = bold_reps,
				slices = slices_per_volume
				)

			parent_path, scan_dir = os.path.split(path)
			#yaml_output = open(os.path.join(parent_path, scan_dir + ".yaml"), 'w')
			print "Will write yaml file to ", os.path.join(parent_path, scan_dir + ".yaml")
			print yaml.dump(yaml_hash, default_flow_style=False)
			#yaml_output.write(yaml.dump(yaml_hash, default_flow_style=False))
			#yaml_output.close()

	# Get the 'long' description of a scan from the database, i.e. something like
	# "GW3D: Sag T2-xeta (FRFSE)"
#	def get_series_long_description(self, path):
#		cursor = DB.cursor()
#		cursor.execute("select series_description from image_datasets where path= ?", (path,))
#		results = list(cursor)
#		cursor.close()
#		if len(results) > 1:
#			raise Exception, "Too many results from path query."
#		result = results[0][0]
#		print result
#		return result

	#Return as a 2-tuple the "short" description of the scan type (eg T2_Flair), and
	# the 'anat_type'; either epan fse, or a few others.
	def get_series_details(self, long_series_description):
		cursor = DB.cursor()
		cursor.execute("SELECT short_description, anat_type FROM series_descriptions WHERE long_description = ?", (long_series_description, ))
		result = list(cursor)[0]
		cursor.close()
		return result

	# Get and return the values for a path that will go into making up the yaml file
	# describing how to process that path.
	def make_yaml_hash(self, scan_path, series_description, anat_type, glob, prefix, output_dir, output_file, short_description, bold_reps, slices):
		if anat_type == "anat":
			result = dict(
				input_dir = scan_path,
				output_dir = output_dir,
				recon_type = "anat",
				prefix = prefix,
				dcmglob = glob,
				anat_type = anat_type,
				modality = short_description,
				output_file = output_file
				)
		else: # anat_type = fmri
			result = dict(
				input_dir = scan_path,
				output_dir = output_dir,
				recon_type = "fmri",
				modality = short_description,
				prefix = prefix,
				repetition_time = '2000',
				dcmglob = glob,
				slices = slices,
				bold_reps = bold_reps,
				skip = 3,
				output_file = output_file
			)
		if result["output_file"] == None: del result["output_file"]
		return result


	####################################################################
	## Methods to do with processing data
	####################################################################
	# Used for testing on local directories; doesn't use the database
	def process_visit_directory2(self):
		for f in os.listdir(self.visit_dir):
			subdir = os.path.join(self.visit_dir, f)
			if not os.path.isdir(subdir): continue
			print "Processing ", subdir
			yaml_path = os.path.join(self.visit_dir, f + ".yaml")
			if not os.path.exists(yaml_path): continue
			self.load_yaml(yaml_path)

			# Do the processing
			self.logfile = open(os.path.join(self.Y["output_dir"], "preproc_anat.bsh"), 'a')
			if self.Y["recon_type"] == 'anat':
				self.do_anat()
			elif self.Y["recon_type"] == 'fmri':
				self.do_fmri()
			else:
				raise Exception, "Unrecognized recon type " + self.Y["recon_type"]
			self.logfile.close()

	# Production version of above function; uses the database.
	def process_visit_directory(self):
		# Find the id of the given visit
		CURSOR.execute("SELECT id FROM visits WHERE path=?", (self.visit_dir,))
		visit_id = CURSOR.fetchall()[0][0]
		# Find the paths for all of the scans associated with that visit.
		CURSOR.execute("SELECT path FROM image_datasets WHERE visit_id=?", (visit_id,))
		for (path,) in list(CURSOR):
		#for path in ["/visit-dir/foo/S4"]:
			parent_path, scan_dir = os.path.split(path)
			yaml_input = os.path.join(parent_path, scan_dir + ".yaml")
			print "Will read yaml file from ", os.path.join(parent_path, scan_dir + ".yaml")
			if not os.path.exists(yaml_input): raise Exception, "Can't load yaml processing directives file."
			load_yaml(yaml_input)

			# Do the processing
			self.logfile = open(os.path.join(self.Y["output_dir"], "preproc_anat.bsh"), 'a')
			if self.Y["recon_type"] == 'anat':
				self.do_anat()
			elif self.Y["recon_type"] == 'fmri':
				self.do_fmri()
			else:
				raise Exception, "Unrecognized recon type " + self.Y["recon_type"]
			self.logfile.close()

	# Load the YAML file, perform some checks, and massage some entries.
	def load_yaml(self, yaml_file):
		input = open(yaml_file, 'r')
		self.Y = yaml.load(input)
		self.Y['visit_dir'] = self.visit_dir
		#### ANAT #####
		if self.Y["recon_type"] == 'anat':
			# Check to make sure the self.YAML file has all the required info.
			required_entries = YamlProcessor.ANAT_YAML_ENTRIES - set(self.Y.keys())
			if len(required_entries) > 0:
				print "Missing entries in self.YAML file:", list(required_entries)
				sys.exit(1)
			# If no output file was specifically provided, construct one.
			self.Y["output_file"] = self.make_unique_nii_filename(self.Y["output_dir"], self.Y.get("output_file", "%(prefix)s_%(modality)s.nii" % self.Y))
		#### FMRI #####
		elif self.Y["recon_type"] == 'fmri':
			# Check to make sure the self.YAML file has all the required info.
			required_entries = YamlProcessor.FMRI_YAML_ENTRIES - set(self.Y.keys())
			if len(required_entries) > 0:
				print "Missing entries in self.YAML file:", list(required_entries)
				sys.exit(1)
			# Fill in skip if it's not provided
			self.Y["skip"] = int(self.Y.get("skip", 0))
			self.Y["bold_reps_minus_skip"] = int(self.Y["bold_reps"]) - self.Y["skip"]
			# If no output file was specifically provided, construct one.
			self.Y["output_file"] = self.make_unique_nii_filename(self.Y["output_dir"], self.Y.get("output_file", "%(prefix)s.nii" % self.Y))
		else:
			raise Exception, "Unrecognized recon type " + self.Y["recon_type"]


	# Given an output dir and a filename ending with .nii,
	# return a filename that does not conflict with the given filename
	# in the given dir. This is done by adding numbers before the .nii, eg
	# foo.nii, foo1.nii, foo2.nii, etc.
	#
	# Filenames that do not end with .nii will be returned unchanged
	def make_unique_nii_filename(self, output_dir, output_file):
		if not output_file.endswith(".nii"): return output_file
		file = os.path.join(output_dir, output_file)
		if not os.path.exists(file): return output_file
		count = 1
		output_file2 = output_file[:-4] + str(count) + output_file[-4:]
		file = file = os.path.join(output_dir, output_file2)
		while os.path.exists(file):
			# put the output number before the .nii prefix
			output_file2 = output_file[:-4] + str(count) + output_file[-4:]
			file = file = os.path.join(output_dir, output_file2)
			count = count + 1
		return output_file2

	def do_anat(self):
		os.environ['AFNI_SLICE_SPACING_IS_GAP']="NO"
		self.execute("to3d -session %(output_dir)s -prefix %(output_file)s -%(anat_type)s %(visit_dir)s/%(input_dir)s/%(dcmglob)s" % self.Y,
			"Error in to3d.")

	def do_fmri(self):
		# Produce the nifti file.
		self.execute("to3d -session %(output_dir)s -prefix %(output_file)s -anat -time:zt %(slices)s %(bold_reps)s %(repetition_time)s seqplus %(visit_dir)s/%(input_dir)s/'%(dcmglob)s'" % self.Y,
			"Error in 'to3d'.")

		# strip the first skip volumes off of the .nii file.
		if self.Y["skip"] > 0:
			self.execute('avwroi %(output_dir)s/%(output_file)s %(output_dir)s/%(output_file)s %(skip)s %(bold_reps_minus_skip)s' % self.Y,
				"Error in avwroi.")

	# Process the given command, logging it to the logfile and writing it to stdout.
	# If an error occurs (the command returns nonzero), raise the given error message.
	def execute(self, cmd, error_message):
		self.logfile.write(cmd)
		print cmd
		process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		(stdout, stderr) = process.communicate()
		print stdout
		print stderr
		self.logfile.write(stdout)
		self.logfile.write(stderr)
		if not process.returncode == 0:
			raise Exception, error_message

def make_yaml_files():
	op = optparse.OptionParser()
	op.add_option("--visit-dir")
	op.add_option("--output-dir")
	op.add_option("--output-file")
	op.add_option("--prefix")
	options, args = op.parse_args()
	if len(args) >0:
		print "All arguments to this command should be named. Type <command-name> --help for help."
		sys.exit(1)
	if options.visit_dir == None:
		print "The --visit-dir argument is required."
		sys.exit(1)
	print options.visit_dir
	yp = YamlProcessor(options.visit_dir)
	yp.create_yaml_files(options)

def process_directory(visit_dir):
	yp = YamlProcessor(visit_dir)
	yp.process_visit_directory()

if __name__ == "__main__":
	if sys.argv[0].endswith("dicom_yaml_process.py"):
		process_directory(os.path.normpath(sys.argv[1]))
	else:
		make_yaml_files()

#d = {"a": 1, "b": "2"}
#print "DUMP", yaml.dump(d, default_flow_style=False)

#ld = get_series_long_description("/Data/vtrak1/raw/wrap140/2501_5917_03042008/013")
#print get_series_details(ld)

