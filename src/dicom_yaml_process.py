#!/usr/bin/env python

import os, sys
import sqlite3, yaml
import subprocess
import optparse
from tempfile import mkdtemp
import shutil

DBPATH = "/Data/home/ken/Projects/development.sqlite3"
DB = sqlite3.connect(DBPATH)
CURSOR = DB.cursor()

class YamlProcessor:

	# Required entires for a self.YAML files where recon_type = 'anat'
	ANAT_YAML_ENTRIES = set(["output_dir", "prefix", "modality", "anat_type", "input_dir", "dcmglob", "ignore"])
	# Required entires for a self.YAML files where recon_type = 'fmri'
	FMRI_YAML_ENTRIES = set(["output_dir", "prefix", "bold_reps", "repetition_time", "input_dir", "slices", "dcmglob", "ignore"])

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
		CURSOR.execute('SELECT id FROM visits WHERE path=?', (self.visit_dir,))
		visit_id = CURSOR.fetchall()[0][0]
		# Find the details for all of the scans associated with that visit.
		CURSOR.execute("SELECT series_description, path, glob, bold_reps, slices_per_volume FROM image_datasets WHERE visit_id=?", (visit_id,))
		# Go through the scans and create the yaml files.
		for series_description, path, glob, bold_reps, slices_per_volume in list(CURSOR):
			short_description, anat_type, ignore = self.get_series_details(series_description)
			if ignore == "Ignore": continue

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
			yaml_output = open(os.path.join(parent_path, scan_dir + ".yaml"), 'w')
			print "Will write yaml file to ", os.path.join(parent_path, scan_dir + ".yaml")
			print yaml.dump(yaml_hash, default_flow_style=False)
			yaml_output.write(yaml.dump(yaml_hash, default_flow_style=False))
			yaml_output.close()

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
		#print "SELECT short_description, anat_type FROM series_descriptions WHERE long_description = %s" % (long_series_description, )
		cursor.execute("SELECT short_description, anat_type, ignore FROM series_descriptions WHERE long_description = ?", (long_series_description, ))
		result = list(cursor)[0]
		cursor.close()
		return result

	# Get and return the values for a path that will go into making up the yaml file
	# describing how to process that path.
	def make_yaml_hash(self, scan_path, series_description, anat_type, glob, prefix, output_dir, output_file, short_description, bold_reps, slices):
		if anat_type in ["anat", "fse"]:
			result = dict(
				input_dir = scan_path,
				output_dir = output_dir,
				recon_type = "anat",
				prefix = prefix,
				dcmglob = glob,
				anat_type = str(anat_type),
				modality = str(short_description),
				output_file = output_file,
				ignore = 'no'
				)
		else: # anat_type = fmri
			result = dict(
				input_dir = scan_path,
				output_dir = output_dir,
				recon_type = "fmri",
				modality = str(short_description),
				prefix = prefix,
				repetition_time = '2000',
				dcmglob = glob,
				slices = slices,
				bold_reps = bold_reps,
				skip = 3,
				output_file = output_file,
				ignore = 'no'
			)
		if result["output_file"] == None: del result["output_file"]
		return result


	####################################################################
	## Methods to do with processing data
	####################################################################
#	# Used for testing on local directories; doesn't use the database
#	def process_visit_directory2(self):
#		for f in os.listdir(self.visit_dir):
#			subdir = os.path.join(self.visit_dir, f)
#			if not os.path.isdir(subdir): continue
#			print "Processing ", subdir
#			yaml_path = os.path.join(self.visit_dir, f + ".yaml")
#			if not os.path.exists(yaml_path): continue
#			self.load_yaml(yaml_path)
#			# Do the processing
#			self.logfile = open(os.path.join(self.Y["output_dir"], "preproc_anat.bsh"), 'a')
#			if self.Y["recon_type"] == 'anat':
#				self.copy_unzip_and_do("%(visit_dir)s/%(input_dir)s" % self.Y, self.do_anat2)
#				#self.do_anat()
#			elif self.Y["recon_type"] == 'fmri':
#				self.copy_unzip_and_do("%(visit_dir)s/%(input_dir)s" % self.Y, self.do_fmri2)
#				#self.do_fmri()
#			else:
#				raise Exception, "Unrecognized recon type " + self.Y["recon_type"]
#			self.logfile.close()

	# Production version of above function; uses the database.
	def process_visit_directory(self):
		# Find the id of the given visit
		self.yaml_summary = {}
		#print "SELECT id FROM visits WHERE path=%s" % (self.visit_dir,)
		CURSOR.execute("SELECT id FROM visits WHERE path=?", (self.visit_dir,))
		visit_id = CURSOR.fetchall()[0][0]
		# Find the paths for all of the scans associated with that visit.
		CURSOR.execute("SELECT path FROM image_datasets WHERE visit_id=?", (visit_id,))
		for (path,) in list(CURSOR):
			parent_path, scan_dir = os.path.split(path)
			yaml_input = os.path.join(parent_path, scan_dir + ".yaml")
			print "Will read yaml file from ", os.path.join(parent_path, scan_dir + ".yaml")
			if not os.path.exists(yaml_input): continue
			self.load_yaml(yaml_input)

			# Things we're not interested in processing.
			if self.Y["dcmglob"] == "":
				continue
			if self.Y['ignore'] == "yes":
				continue

			# Do the processing
			self.logfile = open(os.path.join(self.Y["output_dir"], "logfile"), 'a')
			self.errorfile = os.path.join(self.Y["output_dir"], "ERRORS.log")
			self.errors = open(self.errorfile, 'a')
			if self.Y["recon_type"] == 'anat':
				self.copy_unzip_and_do("%(input_dir)s" % self.Y, self.do_anat2, "Problem encountered processing %(input_dir)s" % self.Y)
			elif self.Y["recon_type"] == 'fmri':
				self.copy_unzip_and_do("%(input_dir)s" % self.Y, self.do_fmri2, "Problem encountered processing %(input_dir)s" % self.Y)
			else:
				raise Exception, "Unrecognized recon type " + self.Y["recon_type"]
			self.logfile.close()
		self.logfile = open(os.path.join(self.Y["output_dir"], "logfile"), 'a')
		self.logfile.write("\n\nYAML FILE SUMMARY:\n")
		self.logfile.write(yaml.dump(self.yaml_summary, default_flow_style=False))
		self.logfile.close()
		if os.path.getsize(self.errorfile) == 0: os.path.remove(self.errorfile)

	# Load the YAML file, perform some checks, and massage some entries.
	def load_yaml(self, yaml_file):
		input = open(yaml_file, 'r')
		self.Y = yaml.load(input)
		self.yaml_summary[str(yaml_file)] = self.Y
		self.Y['visit_dir'] = self.visit_dir
		print "YAML FILE %s (+ additions) IS:" % (yaml_file,)
		print yaml.dump(self.Y, default_flow_style=False)
		#### ANAT #####
		if self.Y['ignore'] == 'yes':
			return
		elif self.Y["recon_type"] == 'anat':
			# Check to make sure the self.YAML file has all the required info.
			required_entries = YamlProcessor.ANAT_YAML_ENTRIES - set(self.Y.keys())
			if len(required_entries) > 0:
				print "Missing entries in self.YAML file:", list(required_entries)
				sys.exit(1)
			# If no output file was specifically provided, construct one.
			self.Y["output_file"] = self.make_unique_nii_filename(self.Y["output_dir"], self.Y.get("output_file", "%(prefix)s%(modality)s.nii" % self.Y))
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
			self.Y["output_file"] = self.make_unique_nii_filename(self.Y["output_dir"], self.Y.get("output_file", "%(prefix)s%(modality)s.nii" % self.Y))
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

	# 'process' is a function which takes an input directory of dicoms as arguments,
	# and performs processing on them. It is up to 'process' to decide what to do
	# with the results.
	def copy_unzip_and_do(self, source_dir, process, error_message):
		try:
			tmp_dir = mkdtemp()
			for f in os.listdir(source_dir):
				dest = os.path.join(tmp_dir, f)
				shutil.copy(os.path.join(source_dir, f), dest)
				if dest.endswith(".bz2"):
					os.system("bunzip2 " + dest)
			try:
				process(tmp_dir)
			except:
				self.errors.write("\n"+error_message)
		finally:
			os.system("rm -r %s" % (tmp_dir,))


#	def do_anat(self):
#		os.environ['AFNI_SLICE_SPACING_IS_GAP']="NO"
#		self.execute("to3d -session %(output_dir)s -prefix %(output_file)s -%(anat_type)s %(visit_dir)s/%(input_dir)s/'%(dcmglob)s'" % self.Y,
#			"Error in to3d.")

	def do_anat2(self, input_dir):
		os.environ['AFNI_SLICE_SPACING_IS_GAP']="NO"
		#print self.Y
		self.execute(("to3d -session %(output_dir)s -prefix %(output_file)s -%(anat_type)s '"+ input_dir + "/%(dcmglob)s'") % self.Y,
			"Error in to3d.")

	def do_fmri2(self, input_dir):
		# Produce the nifti file.
		self.execute(("to3d -session %(output_dir)s -prefix %(output_file)s -anat -time:zt %(slices)s %(bold_reps)s %(repetition_time)s seqplus '"+ input_dir + "/%(dcmglob)s'") % self.Y,
			"Error in 'to3d'.")

		# strip the first skip volumes off of the .nii file.
		if self.Y["skip"] > 0:
			self.execute('avwroi %(output_dir)s/%(output_file)s %(output_dir)s/%(output_file)s %(skip)s %(bold_reps_minus_skip)s' % self.Y,
				"Error in avwroi.")

#	def do_fmri(self):
#		return
#		# Produce the nifti file.
#		self.execute("to3d -session %(output_dir)s -prefix %(output_file)s -anat -time:zt %(slices)s %(bold_reps)s %(repetition_time)s seqplus %(visit_dir)s/%(input_dir)s/'%(dcmglob)s'" % self.Y,
#			"Error in 'to3d'.")
#
#		# strip the first skip volumes off of the .nii file.
#		if self.Y["skip"] > 0:
#			self.execute('avwroi %(output_dir)s/%(output_file)s %(output_dir)s/%(output_file)s %(skip)s %(bold_reps_minus_skip)s' % self.Y,
#				"Error in avwroi.")

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

def do_main():
	usage = """If the --make-yaml-files option is given, the full range of options
may be used. If it is not given, only the --visit-dir options should be used; this
will result in the files being processed.

You must prepare a directory using --make-yaml-files before you can process it without."""
	op = optparse.OptionParser(usage = usage)
	op.add_option("-v", "--visit-dir", help="Full path to directory being processed, eg. '/Data/vtrak1/raw/alz_2000/alz122'")
	group = optparse.OptionGroup(op, "Options for use iwth --make-yaml-files:")
	group.add_option("-m", "--make-yaml-files", action="store_true", help="If true,"\
		" the YAML files will be generated for visit_dir."\
		"If false, the file processing will be done.")
	group.add_option("-d", "--output-dir", help="Where processed files will be placed")
	group.add_option("-f", "--output-file", help="Optional argument that overrides normal file name construction.")
	group.add_option("-p", "--prefix", help="output file name prefix.", default="")
	op.add_option_group(group)
	options, args = op.parse_args()
	if len(args) >0:
		print "All arguments to this command should be named. Type <command-name> --help for help."
		sys.exit(1)
	if options.visit_dir == None:
		print "The --visit-dir argument is required. Use --help for full help."
		sys.exit(1)
	yp = YamlProcessor(options.visit_dir)
	if options.make_yaml_files:
		yp.create_yaml_files(options)
	else:
		yp.process_visit_directory()
		

if __name__ == "__main__":
	do_main()
