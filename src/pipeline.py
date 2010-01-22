#!/usr/bin/env python

from optparse import OptionParser
import tempfile, shutil, os, tempfile, subprocess, sys, re
os.environ["FSLOUTPUTTYPE"]="NIFTI"

class Pipeline(object):
	DCM2NII_PATH='/apps/mricron/dcm2nii '  # Used for dicom > nii file conversion.
	TO3D_PATH='to3d '
	FSLPATH = '/apps/fsl_dists/fsl-3.3.11_64/bin/'

	## Each of these indicates one step in the pipeline process.
	STEPS = [
		'init','recon','stc','realign','motion','derivs','fmap','norm','stats'
	]

	## Each flagname is used as the name of an empty file that is written into
	# the 'preproc' dir, to indicate that a step in the pipeline has been completed.
	# This prevents unnecessary reprocessing.
	FLAGNAMES = [
		'INITIALIZATION','DONE_RECONSTRUCTION','DONE_STC','DONE_REALIGNMENT',
		'DONE_MOTION_CHECK', 'DONE_CALC_DERIVS','DONE_FIELD_MAP',
		'DONE_NORM_SMOOTH','DONE_STATS1'
	]

	## This dictionary associates step names with file flag names. At the completion
	# of a named step, the associated flagname will be looked up in this directory,
	# and an empty file of that name will be created in the preproc directory.
	FLAGS = dict( zip(STEPS, FLAGNAMES) )

	def __init__(self, subid, rawdir, anatdir, preprocdir, statsdir):
		## Subject id.
		self.subid = subid
		## Raw directory, holding initial primary data files.
		self.rawdir = rawdir
		## Directory that is sometimes present, holding further input data files.
		self.anatdir = anatdir
		## Directory in which processing is mostly done.
		self.preprocdir = preprocdir
		## Directory in which stats1 processing is done.
		self.statsdir = statsdir

		self.working_preprocdir = os.path.abspath(os.path.join('/Data/tmp', self.subid ) )
		self.working_rawdir = os.path.join(self.working_preprocdir, 'dicoms')
		self.working_anatdir = os.path.join(self.working_rawdir, 'raw')

		self.fmapdir = None
		self.logfile = os.path.join(self.preprocdir, subid + '_pipeline.log')
		
		# Create a dict for misc. program configuration variables.
		self.config = {}
		
		# Default to SPM5 at __init__
		self.config['spm_version'] = 'spm5'

		## Not yet used, but can be used in the future to track what files are
		# produced at what steps.
		self.step_files = dict( zip(self.STEPS, [None]*len(self.STEPS)) )
		
		formatstr = "%-25s : %s"
		print """
		#####################################################
		#                                                   #
		#   Welcome to the Johnson Lab fMRI Pipeline        #
		#                                                   #
		#####################################################
		"""
		print formatstr % ("Subject ID", self.subid)
		print formatstr % ("Raw directory", self.rawdir)
		print formatstr % ("Anatomicals directory", self.anatdir)
		print formatstr % ("Preprocessing directory", self.preprocdir)
		print formatstr % ("Stats directory", self.statsdir)
		print formatstr % ("Logfile", self.logfile)
		print

	## Auxiliary function, used in assembling MatLab commands, which are then run by
	# another piece of code.
	def runMatlab(self, arg):
		return 'matlab7 -nodesktop -nosplash -r "addpath %s; %s; exit"' % (self.spm_path(), arg, )
	## Auxiliary function, used in assembling SPM commands, which are then run by
	# another piece of code.
	def runSPMJob(self, arg):
		return self.runMatlab("spm_jobman('run_nogui','%s')" % (arg, ))
	## Auxiliary function, used to provide SPM path from setting or config.
	def spm_path(self):
		if 'spm_path' in self.config: 
			spm_path = self.config['spm_path']
		else:
			spm_path = "/apps/spm/%s_current" % self.config['spm_version']
		return spm_path
			

	## Checks for proper directory setup.  Raw, preproc, and stats directories
	# must exist before running this pipeline.
	def checkSetup(self):
		# Check to ensure the given raw, preproc, and stats dirs exist
		if not os.path.isdir(self.rawdir):
			raise IOError("ERROR: raw directory given does not exist.")

		self.prepareLocalCopy()

		if not os.path.isdir(self.preprocdir):
			raise IOError("ERROR: preproc directory given does not exist.")
		if self.statsdir and not os.path.isdir(self.statsdir):
			raise IOError("ERROR: stats directory given does not exist.")

		self.step_files['init'] = set( os.listdir(self.working_preprocdir) )
		
	## Copies and unzips raw files to a faster local working directory. 
	def prepareLocalCopy(self):
		## Create a new working directory at initialization to do processing as locally as possible.
		# In Development - Use a "constant" temp directory.

		if not os.path.isdir(self.working_preprocdir): os.mkdir(self.working_preprocdir)
		# In Production - Use a real temp directory.
		#self.working_preprocdir = os.path.abspath( tempfile.mkdtemp(dir = '/tmp') )
		
		# Store the local copy of unzipped raw files in a "dicoms" folder inside the working preproc directory.

		formatstr = "%-35s : %s"
		print formatstr % ("Working / Local Preproc Directory", self.working_preprocdir)
		print formatstr % ("Working / Local Raw Directory", self.working_rawdir )

	def log(self, msg):
		"""Append a message to the logfile, and print it to the screen also"""
		output = open(self.logfile, 'a')
		output.write(msg + '\n')
		output.close()
		print msg

	## Queries to see if an empty file of a given name exists; such a file indicates
	# a previous step in the image processing pipeline completed successfully.
	def isDone(self, step):
		return os.path.exists(os.path.join(self.working_preprocdir, self.FLAGS[step]))

	## Creates an empty file of a given name, to indicate that a particular step
	# in the pipeline has been completed.
	def setDone(self, step):
		donefile = open(os.path.join(self.working_preprocdir, self.FLAGS[step]), 'w')
		donefile.close()

	def removeStep(self, step):
		for file in self.step_files[step]:
			os.remove(os.path.join(self.preprocdir, file))

	## Runs an external (shell) command, prints info to the screen, logs output
	# of the command, and returns the return code of the external command.
	def run(self, cmd):
		self.log('<shell command>: ' + cmd)
		sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
		sp.wait()
		self.log(sp.stdout.read())
		return sp.returncode
		
	
	## Copy a Directory Tree and decompress any zipped images. 
	#  Used to create a local copy of unziped raw data.
	#  Raises an Error if the Destination directory exists.
	def copyAndUnzip(self, src, dst):
		def ignoreFiles(dir, files):
			if dir != src: return []
			matcher = re.compile("^((\d\d\d)|[sS]\d|[Pr]).*")
			matches = [f for f in files if matcher.match(f)]
			ignored = list(set(files) - set(matches))
			print "Ignoring ", ignored
			return ignored
			
		src = os.path.abspath(src)
		dst = os.path.abspath(dst)
		print src, dst
		if os.path.exists(dst):
			# shutil.copytree will not overwrite directories, so the destination directory cannot exist.
			raise IOError("THE DESTINATION DIRECTORY CANNOT EXIST.  Program terminating.")
		shutil.copytree(src, dst, True, ignoreFiles)
		for (path, dirnames, filenames) in os.walk(dst):
			for f in filenames:
				file = os.path.join(path, f)
				if file.endswith(".bz2"):
					os.system("bunzip2 %s" % (file,))

	# Remove Discarded Acquisitions from nifti image files using avwroi
	# Raises an IOError if the image does not exist.
	# If no output file is given, the image is stripped in place.
	def remove_discdacqs(self, image, numberToRemove, outputFile = False):
		print "++++++ Removing " + str(numberToRemove) + " Discarded Acquistions from " + image + " ++++++"
		image = os.path.abspath(image)
		if not os.path.exists(image): raise IOError("Image does not exist.")
		if not outputFile: outputFile = image

		numberToRemove = int(numberToRemove)
		p1 = subprocess.Popen(["fslinfo", image], stdout=subprocess.PIPE)
		p2 = subprocess.Popen(["grep","dim4"], stdin = p1.stdout, stdout = subprocess.PIPE)
		output = p2.communicate()[0]
		totalReps = int(output.strip().split()[1])
		print "Current Reps: " + str(totalReps)
		repSize = totalReps - numberToRemove
		cmd = "fslroi " + image + " " + outputFile + " " + str(numberToRemove) + " " + str(repSize) # fslroi is 0-indexed.
		print cmd
		os.system(cmd)
					
	
	
	#######  Begin Pipeline Steps  #############
	
	## Run the reconstrunction step of the pipeline
	def recon(self, study_name, functional_format, task_order=None, pfile_order=None, refdat_order=None):

		if self.isDone('recon'):
			print "++++++ Reconstruction already done ++++++"
			return

		files_before_this_step = set( os.listdir(self.working_preprocdir) )

		if not os.path.isdir(self.working_rawdir ): self.copyAndUnzip(self.rawdir, self.working_rawdir)
		
		if functional_format == 'dicoms': self.convert_all_dicom_files()
		else: self.recon_pfiles(task_order, pfile_order, study_name, refdat_order)

		self.setDone('recon')
		self.step_files['recon'] = set( os.listdir(self.preprocdir) ) - files_before_this_step


	def recon_pfiles(self, task_order, pfile_order, study_name, refdat_order):
		"""Uses the epirecon_ex command to perform a reconstruction on input files.
		Results are left in the 'preproc' directory.
		Task and Pfiles must be passed in as tuples, a tuple of ref.dat files is optional."""

		# Do some basic Reconstruction Sanity Checking
		self.log("++++++ Reconstructing raw data ++++++")
		if len(task_order) != len(pfile_order):
			raise "Bad number of pfiles."
		if refdat_order:
			if len(task_order) != len(refdat_order):
				raise "Bad number of refdat files."

		files_to_check = []
		for pfile in pfile_order:
			files_to_check.append(os.path.join(self.working_anatdir, pfile))
		if refdat_order:
			for refdatfile in refdat_order:
				refdatpath = os.path.join(self.rawdir, refdatfile)
				if not os.path.exists(refdatpath):
					raise IOError("Can't find file '" + refdatpath + "'.")
		for filepath in files_to_check:
			if not os.path.exists(filepath):
				raise IOError("Can't find file '" + filepath + "'.")

		## Setup a temp directory to organize our
		#  files for reconstruction.
		temp_dir = os.path.abspath( tempfile.mkdtemp(dir = '/tmp') )
		os.chdir(self.working_preprocdir)

		## If refdat files were passed in along with task & pfile, then
		# unzip them all together.
		#
		# Otherwise just uznip task & pfiles, and determinerefdat file from
		# simple heuristics inside the recon.
		if refdat_order:
			for task, pfile, refdatfile in zip(task_order, pfile_order, refdat_order):
				self.recon_one_pfile(temp_dir, task, pfile, study_name, refdatfile )
		else:
			for task, pfile in zip(task_order, pfile_order):
				self.recon_one_pfile(temp_dir, task, pfile, study_name)

		# Clean up and setDone and step_files
		shutil.rmtree(temp_dir)

	## Find a ref.dat file. This involves several simple heuristics.
	def findRefDatFile(self, study_name, search_directory = None):
		if not search_directory:
			search_directory = self.working_anatdir
			
		# Find an appropriate ref.dat file. First we look for some specific name patterns.
		possibilities = [os.path.join(search_directory, "ref.dat"),
						 os.path.join(search_directory, "ref.dat." + study_name + '.' + self.subid[1:]),
						 os.path.join(search_directory, "ref.dat." + self.subid),
		                                 os.path.join(search_directory, "ref.dat." + study_name + '.' + self.subid),]
		refdatfile = None

		for f in possibilities:
			if os.path.isfile(f):
				refdatfile = f
				break

		## Finally, if we couldn't find a file using the above name patterns, we
		#  look to see if there if there is just one file starting with
		#  "ref.dat". If there is more than one and nothing was passed in,
		#  the situation is ambiguous, and we'll raise an error
		if not refdatfile:
			refdatfile = [ f for f in os.listdir(search_directory) if f.startswith("ref.dat") ]
			if len(refdatfile) != 1:
				raise "Couldn't find an appropriate ref.dat file in " + self.rawdir
			else:
				refdatfile = os.path.abspath( os.path.join(search_directory, refdatfile[0]) )

		return refdatfile

	def recon_one_pfile(self, temp_dir, task, pfile, study_name, refdatfile=None):
		"""Reconstructs a single pfile into the epirecon default brik/head when
		given a temporary working directory, path to the pfile and the task to
		use when naming the output."""
		raw_pfile = os.path.join(self.working_anatdir, pfile)
		tmp_pfile = os.path.join(temp_dir, pfile)
		os.symlink( raw_pfile, tmp_pfile )

		## Finds an appropriate ref.dat file if one wasn't passed in;
		#  raises an exception if not found
		if refdatfile:
			refdatfile = os.path.join(self.working_anatdir, refdatfile)
		else:
			refdatfile = self.findRefDatFile(study_name)

		## Create a link in the temporary working directory called "ref.dat"
		#  that points to the correct ref.dat* to use for this pfile's reconstruction.
		tmp_refdatfile = os.path.join(temp_dir, "ref.dat")
		os.symlink(refdatfile, tmp_refdatfile)

		self.log("### Reconstructing task: %s using Pfile: %s and refdat file %s ###" % (task, tmp_pfile, tmp_refdatfile))
		epirecon_cmd_tplt = "epirecon_ex -f %s -skip 3 -NAME %s_%s -scltype=0"
		epirecon_cmd = epirecon_cmd_tplt % (tmp_pfile, self.subid, task)
		returncode = self.run(epirecon_cmd)
		if returncode:
			raise "There was a problem with Reconstruction."


		## Clear the ref.dat link after each reconstruction since we are
		#  finding a new one for each pfile.
		os.remove(tmp_refdatfile)

	def convert_all_dicom_files(self):
		""" Default Conversion from Dicom to Nifti."""
		print "Converting dicoms in " + self.working_rawdir + " to " + self.working_preprocdir
		self.convert_dicom_files(self.working_rawdir, self.working_preprocdir)

	def convert_dicom_files(self, input_dir, output_dir = '/tmp'):
		""" Walk through all the directories in input_dir and create niftis in the output dir using dcm2nii."""
		input_dir = os.path.abspath(input_dir)

		if os.path.exists(os.path.join(output_dir, "preproc_anat.bsh")):
			print "Executing existing preproc_anat.bsh..."
			#TODO Add a Catch in case the file is owned by another user and
			#     cannot be changed to executible.

			os.chmod(os.path.join(output_dir, "preproc_anat.bsh"), 0775)
			#self.run(os.path.join(output_dir, "preproc_anat.bsh")) # Using self.run (using subprocess) hangs.
			os.system(os.path.join(output_dir, "preproc_anat.bsh"))
		else:
			print "Converting " + input_dir + "..."
			sys.path.append("/Data/data1/lab_scripts")
			preproc_anat_cmd =  "preproc_anat.sh " + input_dir + " " + output_dir + " " + self.subid + " fmri"

			os.system(preproc_anat_cmd) # Using self.run (using subprocess) hangs this step.
			self.run("gunzip " + output_dir + "/*.gz")

	def to_nii(self, input_dir, output_dir = '/tmp'):
		""" Convert the dicom files in input_dir and spit out a nifti file in output dir. """
		print "Converting dicoms in " + input_dir
#		self.run(self.DCM2NII_PATH + '-d n -e n -g n -i n -o ' + output_dir + " " + input_dir )
		self.run(self.TO3D_PATH + ' -session ' +  output_dir + ' -prefix ' + self.subid + "_" + os.path.basename(input_dir) + " " + input_dir + '/*.dcm')


	## Run the STC step of the pipeline.
	def stc(self, functional_format = 'pfiles'):
		files_before_this_step = set( os.listdir(self.working_preprocdir) )
			
		print "++++++ Running Slice-time Correction ++++++"

		if functional_format == 'pfiles':
			infiles = [ os.path.join(self.working_preprocdir, f[:-5]) for f in os.listdir(self.working_preprocdir) if f.endswith(".HEAD") ]
			outfiles = [ os.path.join(self.working_preprocdir, "a" + f[:-10] + ".nii") for f in os.listdir(self.working_preprocdir) if f.endswith(".HEAD") ]
			for infile, outfile in zip(infiles, outfiles):
				if not os.path.exists(outfile):
					shift_cmd = "slicetimer -i " + infile + " -o " + outfile + "--down "
					#shift_cmd = "3dTshift -tzero 0 -prefix %s %s" % (outfile, infile)
					self.run(shift_cmd)
		elif functional_format == 'dicoms':
			infiles = [os.path.splitext(f)[0] for f in os.listdir(self.working_preprocdir) if f.endswith("nii")] # Get the file prefixes for nifti files.
			outfiles =  ["a"+os.path.splitext(f)[0] for f in os.listdir(self.working_preprocdir) if f.endswith("nii")] # Get the file prefixes for nifti files.
			for infile, outfile in zip(infiles, outfiles):
				print infile, outfile
				shift_cmd = "slicetimer -i " + os.path.join(self.working_preprocdir, infile) + " -o " + os.path.join(self.working_preprocdir, outfile) + " --down"
				print os.path.join(self.working_preprocdir, infile), os.path.join(self.working_preprocdir, outfile)
				self.run(shift_cmd)
				
				# FSL does all its native computations in float, which is also the default output type.
				# Float is needlessly twice as big as INT16 (aka short) so we are changing the filetype back to save space.
				change_datatype_cmd = "fslmaths " + outfile + " " + outfile + " -odt short"
				self.run(change_datatype_cmd)
				
		else: raise ValueError, "Unrecognized dicom format."
		
		self.step_files['stc'] = set( os.listdir(self.working_preprocdir) ) - files_before_this_step
        

	## Run the realign step of the pipeline
	def realign(self, realignjob):
		files_before_this_step = set( os.listdir(self.working_preprocdir) )
		if not self.isDone('realign'):
			print "++++++ Running Realignment ++++++"
			jobfile = os.path.abspath(realignjob)
			cmd = self.runSPMJob(jobfile)
			print "Running Job " + cmd			
			os.system(cmd)
			self.setDone('realign')
		else:
			print "++++++ Realignment already done ++++++"
		self.step_files['realign'] = set( os.listdir(self.working_preprocdir) ) - files_before_this_step

	## Run the motion check step of the pipeline
	def motionCheck(self, threshold):
		files_before_this_step = set( os.listdir(self.working_preprocdir) )
		if self.isDone('motion'):
			print "++++++ Motion Check Already Done ++++++"
			return
		print "++++++ Running Motion Check ++++++"
		for f in os.listdir(self.working_preprocdir):
			if f.startswith("rp_") and f.endswith(".txt"):
				infile = os.path.join(self.working_preprocdir, f)
				cmd = self.runMatlab("fmri_motionCheck('%s', '%s')" % (infile, threshold))
				self.run(cmd)
		self.setDone('motion')
		self.step_files['motion'] = set( os.listdir(self.working_preprocdir) ) - files_before_this_step

	## Run the calc derivs step of the pipeline
	def calcDerivs(self):
		files_before_this_step = set( os.listdir(self.working_preprocdir) )
		if self.isDone('derivs'):
			print "++++++ Calc Derivs Already Done ++++++"
			return
		print "++++++ Running Calc Derivs ++++++"
		os.chdir(self.working_preprocdir)
		for f in os.listdir('.'):
			if f.startswith("rp_") and f.endswith(".txt"):
				cmd = self.runMatlab("fmri_calcDerivatives('%s')" % (f, ))
				self.run(cmd)
		self.setDone('derivs')
		self.step_files['derivs'] = set( os.listdir(self.working_preprocdir) ) - files_before_this_step

	## Run the field map step of the pipeline
	def fieldMap(self):
		os.chdir(self.working_preprocdir)
		files_before_this_step = set( os.listdir(self.working_preprocdir) )
		os.system('FieldmapAtWaisman.sh ' + self.subid + ' ' + self.working_preprocdir)
		resulting_files = [ f for f in os.listdir(self.working_preprocdir) if f.startswith('ra') and f.endswith('_fm.nii') ]
		for f in resulting_files:
			self.run( 'avwcpgeom %s %s' % (f.replace('_fm',''), f) )
		self.setDone('fmap')
		self.step_files['fmap'] = set( os.listdir(self.working_preprocdir) ) - files_before_this_step

	## Run the normalization/smoothing step
	def normSmooth(self, normjob):
		files_before_this_step = set( os.listdir(self.working_preprocdir) )
		if self.isDone('norm'):
			print "++++++ Norm/Smooth Already Done ++++++"
			return
		cmd = self.runSPMJob(normjob)
		print "Running Job " + cmd
		os.system(cmd)
		self.setDone('norm')
		self.step_files['norm'] = set( os.listdir(self.working_preprocdir) ) - files_before_this_step

	# Move final files to their network location for stats.
	def moveLocalFilesToNetwork(self):
		files_to_move = set()
		extensions = ['ps', '.mat', '.txt', '.log', '.bsh']

		for file in os.listdir(self.working_preprocdir):
			if file.startswith('sw') or (file.startswith('wa') and file.endswith('nii')):
				files_to_move.add(file)

			for extension in extensions:
				if file.endswith(extension):
					files_to_move.add(file)

		for file in files_to_move:
			try:
				print "Moving " + file + " to " + self.preprocdir
				shutil.move(file, self.preprocdir)
			except shutil.Error as err:
				print "Could not move " + file + " because destination already exists."
				print err

	## Run the stats step
	def stats1L(self, statsjob):
		files_before_this_step = set( os.listdir(self.preprocdir) )
		if self.isDone('stats'):
			self.log("++++++ Stats 1 Already Done ++++++")
			return
		self.log("++++++ Running Stats 1 ++++++")
		cmd = self.runSPMJob(statsjob)
		# NOTE: for some reason, using Popen (via "run") causes a hang. So leave
		# this as a call to "os.system" and forego logging.
		print "Running Job " + cmd
		os.system(cmd)
		self.setDone('stats')
		self.step_files['stats'] = set( os.listdir(self.preprocdir) ) - files_before_this_step

###  END OF PIPELINE CLASS  ###



if __name__ == "__main__":
	print "This file is not intended to be used from the command line."
