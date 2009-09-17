#!/usr/bin/env python
import os

class StudyVariables(object):
################### USERS EDIT THE VARIABLES BELOW##############################
################### TO ADAPT THEM TO YOUR OWN PROJECT. #########################
	protocolName = 'johnson.alz.snodrest.visit2'
	protocolDesc = 'Snod/Rest for alz visit 2'
	studyName = 'alz2'  # Used for finding the ref.dat filename.
	studyPrefix = 'alz' # Used for inflecting filenames for raw files.
	studyFunctionalFormat = 'pfiles'
	studyRawDir = '/Data/vtrak1/raw/alz_2000'
	studyPreprocDir = '/Data/vtrak1/preprocessed/visits/johnson.alz.snodrest.visit2'
	studyStatsDir = '/Data/vtrak1/preprocessed/visits/johnson.alz.snodrest.visit2'
	studyOnsetsDir = None
	studyTemplatesDir = '/Data/vtrak1/preprocessed/progs/johnson.alz.snodrest.visit2/templates'

	realignJobFile = 'johnson.alz.snodrest.visit2_realign.mat'
	realignTemplateSubid = '2017_2'
	realignTemplatePreprocDir = '/Data/tmp'
	realignTemplateRuns = []
	realignTemplateFM = False

	normJobFile = 'johnson.alz.snodrest.visit2_norm.mat'
	normTemplateSubid = 'alz010'
	normTemplatePreprocDir = '/Data/tmp'
	normTemplateRuns = []
	normTemplateFM = False

	#statsJobFile = 'johnson.alz.snodrest.visit2_stats.mat'
	#statsTemplateSubid = 'alz010'
	#statsTemplatePreprocDir = '/Data/vtrak1/preprocessed/visits/johnson.alz.snodrest.visit2'
	#statsTemplateStatsDir = '/Data/vtrak1/preprocessed/visits/johnson.alz.snodrest.visit2'
	#statsTemplateOnsetsDir = None
	#statsTemplateRuns = []
	#statsTemplateFM = False
	#subjectInfoCSV = None

	realignJob = os.path.join(studyTemplatesDir, realignJobFile)
	normJob = os.path.join(studyTemplatesDir, normJobFile)
	#statsJob = os.path.join(studyTemplatesDir, statsJobFile)
######################### DO NOT EDIT BELOW THIS LINE #########################






"""Preprocess a subject

preproc-johnson.alz.snodrest.visit2.py <subject ID> [pipe options]
"""

import sys
import shutil
import glob
sys.path.append('/Data/home/erik/NetBeansProjects/PythonPipeline/src')
sys.path.append('/Data/vtrak1/SysAdmin/production/python')
from optparse import OptionParser
from greccparsers import subject_parse
from spmjobs import *
from pipeline import Pipeline


SUBJECT_INFO_CSV = '/Data/vtrak1/preprocessed/progs/johnson.alz.snodrest.visit2/subject_run_info.csv'
MOTION_THRESHOLD = 1

def makeOptionsParser():
	# Argument/options parsing
	global parser
	parser = OptionParser( usage = __doc__ )
	parser.add_option("-r","--recon",action="store_true",dest="recon",
	    default=False, help="reconstruct images from raw")
	parser.add_option("-s","--stc",action="store_true",dest="stc",
	    default=False, help="slice time correct images")
	parser.add_option("-l","--realign",action="store_true",dest="realign",
	    default=False, help="realign images to correct for motion")
	parser.add_option("-m","--motioncheck",action="store_true",dest="motioncheck",
	    default=False, help="check for excessive motion")
	parser.add_option("-c","--calcderivs",action="store_true", dest="calcderivs",
	    default=False, help="calculate the motion derivatives for regressors")
	parser.add_option("-f","--fieldmap",action="store_true",dest="fmap",
	    default=False, help="perform fieldmap correction")
	parser.add_option("-n","--normalize",action="store_true",dest="normalize",
	    default=False, help="normalize images to EPI template")
	parser.add_option("--move", action="store_true", dest="moveLocalFiles",
		default=False, help="move local files to their final destinations.")
	parser.add_option("-x","--stats",action="store_true",dest="stats",
	    default=False, help="run first level stats")
	parser.add_option("--freshstart",action="store_true",dest="fresh",
	    default=False, help="removes preproc and stats directories, starts fresh.")
	parser.add_option("--wrapper",default="RiesAwareVisit1")
	parser.add_option("--all",action="store_true",dest="all",
		default=False, help="Run Recon, stc, realign, motioncheck, calcderiv, fieldmap, norm, move files and stats.")
	return parser

if (len(sys.argv) == 1):
	args = ["alz010_2", "--all", "--freshstart"]
else: args = sys.argv

(options, args) = makeOptionsParser().parse_args(args)

if (len(args) != 1):
    parser.error("Incorrect number of arguments, subject ID missing.")
subid = args[0]


# retrieves a dictionary of subject specific visit variables from the csv file
subjFunctionalFormat = StudyVariables.studyFunctionalFormat

# retrieves a dictionary of subject specific visit variables from the csv file
subjVisitVars = subject_parse(SUBJECT_INFO_CSV, str(subid))
subjHasFmap = bool(subjVisitVars['hasfmap'][0])
subjTasks = subjVisitVars['tasks']
subjPfiles = subjVisitVars['pfiles']

# For this protocol we are skipping fieldmaps, regardless of whether or not 
# they occured, in order to improve consistency of analysis.
subjHasFmap = False

# Subject Variable Defaults from Hospital:
subjRawDir = glob.glob(os.path.join(StudyVariables.studyRawDir, subid + '*'))[0]
subjAnatDir = os.path.join(subjRawDir, 'raw')
subjPreprocDir = os.path.join(StudyVariables.studyPreprocDir, subid, 'fmri')
if options.stats: 
	subjStatsDir = os.path.join(StudyVariables.studyStatsDir, subid, 'stats')
	statstasks = []
else: 
	subjStatsDir = None
	statstasks = []

subjLonDir = os.path.join(subjPreprocDir, 'lon')


print """
##########################################################
#                                                        #
#    Welcome to the Preprocessing Wrapper script         #
#                                                        #
##########################################################
"""

if options.fresh:
    if options.normalize and os.path.exists(subjPreprocDir): shutil.rmtree(subjPreprocDir)
    if options.stats and os.path.exists(subjStatsDir): shutil.rmtree(subjStatsDir)

if options.all:
    for option in options.__dict__: options.__dict__[option] = True
    
    # Skip some options for protocol johnson.alz.snodrest.visit2 (part of a longitudinal pipe)
    options.fmap = False
    options.stats = False
    

# Check Write Permissions in Subject Paths
paths_to_check_permissions = []
if options.normalize: paths_to_check_permissions.append(subjPreprocDir)
if options.stats: paths_to_check_permissions.append(subjStatsDir)

for path in paths_to_check_permissions:
	if os.path.exists(path):
		if not os.access(path, os.W_OK): raise "Cannot Write to Directory " + path
	else: os.makedirs(path)


# make a pipe, run it.
pipe = Pipeline(subid, subjRawDir, subjAnatDir, subjPreprocDir, subjStatsDir)
pipe.checkSetup()

if options.realign: subjRealignJob = os.path.join(pipe.working_preprocdir, subid+'_realign.mat')
else: subjRealignJob = None

if options.normalize: subjNormJob = os.path.join(pipe.working_preprocdir, subid + '_norm.mat')
else: subjNormJob = None

if options.stats: subjStatsJob = os.path.join(subjStatsDir, subid + '_stats.mat')
else: subjStatsJob = None

print subjNormJob

str = "%-30s : %s"
#print str % ('subid',subid)
#print str % ('subjRawDir',subjRawDir)
#print str % ('subjAnatDir',subjAnatDir)
#print str % ('subjPreprocDir',subjPreprocDir)
#print str % ('subjStatsDir',subjStatsDir)
#print str % ('ALZ2.studyName',StudyVariables.studyName)
#print str % ('subjRealignJob',subjRealignJob)
#print str % ('MOTION_THRESHOLD',MOTION_THRESHOLD)

for nameValue in [('subid',subid),('subjRawDir',subjRawDir),('subjAnatDir',subjAnatDir),
	('subjPreprocDir',subjPreprocDir),('ALZ2.studyName',StudyVariables.studyName),
	('MOTION_THRESHOLD',MOTION_THRESHOLD)
]:
	print "%-30s : %s" % nameValue

if subjNormJob:     print str % ('subjNormJob',subjNormJob)
if subjStatsJob:    print str % ('subjStatsJob',subjStatsJob)
if statstasks:  print str % ('statstasks',statstasks)

# Subject customization occurs only by including subid; otherwise paths do not
# contain subject information.
#
# The path to the working directory (the first half of what is returned from split)
# replaces the subject template directory.

# subject's identity for realignment and normalization
subj_preproc_identity = SPMJobIdentity (
    subid,
    [os.path.split(pipe.working_preprocdir)[0] ],
    statstasks,
    fieldmap= subjHasFmap and options.fmap
)

# subject's identity for stats
subj_stats_identity = SPMJobIdentity (
    subid,
    [StudyVariables.studyPreprocDir, StudyVariables.studyStatsDir, StudyVariables.studyOnsetsDir],
    statstasks,
    fieldmap= subjHasFmap and options.fmap
)

if not os.path.exists(subjRealignJob) and StudyVariables.realignJob and options.realign:
    shutil.copy(StudyVariables.realignJob, subjRealignJob)
    # making a job instance for the template realign job and changing its identity
    realign_template_identity = SPMJobIdentity (
        StudyVariables.realignTemplateSubid,
        [StudyVariables.realignTemplatePreprocDir],
        StudyVariables.realignTemplateRuns,
        fieldmap=StudyVariables.realignTemplateFM
    )
    realign_job = SPMJob(subjRealignJob, realign_template_identity)
    print "Replacing Realign SPM Identity in subject job "; print realign_job
    realign_job.replaceIdentity(subj_preproc_identity)


if not os.path.exists(subjNormJob) and StudyVariables.normJob and options.normalize:
    shutil.copy(StudyVariables.normJob, subjNormJob)
    # make and change norm job instance
    norm_template_identity = SPMJobIdentity(
        StudyVariables.normTemplateSubid,
        [StudyVariables.normTemplatePreprocDir],
        StudyVariables.normTemplateRuns,
        fieldmap=StudyVariables.normTemplateFM
    )
    norm_job = SPMJob(subjNormJob, norm_template_identity)
    print "Replacing Norm SPM Identity in subject job "; print norm_job
    norm_job.replaceIdentity(subj_preproc_identity)


if options.stats:
    if not os.path.exists(subjStatsJob): shutil.copy(StudyVariables.statsJob, subjStatsJob)

    print StudyVariables.statsTemplateSubid
    # make and change stats job instance
    stats_template_identity = SPMJobIdentity (
        StudyVariables.statsTemplateSubid,
        [StudyVariables.statsTemplatePreprocDir, StudyVariables.statsTemplateStatsDir, StudyVariables.statsTemplateOnsetsDir],
        StudyVariables.statsTemplateRuns,
        fieldmap=StudyVariables.statsTemplateFM
    )
    stats_job = SPMJob(subjStatsJob, stats_template_identity)
    print "Replacing Stats SPM Identity in subject job "; print stats_job
    stats_job.replaceIdentity(subj_stats_identity)


current = os.getcwd()
os.chdir(pipe.working_preprocdir)
if options.recon:
    # If we are to do a reconstruction, check to see if the subject had
    # ref.dat files in the subject csv.  If so, pass them in to the pipe reconstruction,
    # otherwise don't.
    if subjVisitVars.has_key('refdat_files'):
        pipe.recon(StudyVariables.studyName, StudyVariables.studyFunctionalFormat, subjVisitVars['tasks'], subjVisitVars['pfiles'], subjVisitVars['refdat_files'])
    else:
        pipe.recon(StudyVariables.studyName, StudyVariables.studyFunctionalFormat,subjVisitVars['tasks'], subjVisitVars['pfiles'] )
    if os.path.exists(subid + '_assetRun1.nii'): pipe.remove_discdacqs(subid + '_assetRun1.nii', 2)
    if os.path.exists(subid + '_assetRun2.nii'): pipe.remove_discdacqs(subid + '_assetRun2.nii', 2)
    if os.path.exists(subid + '_assetRest195.nii'): pipe.remove_discdacqs(subid + '_assetRest195.nii', 32)
    if os.path.exists(subid + '_assetRest165.nii'): pipe.remove_discdacqs(subid + '_assetRest165.nii', 2)
if options.stc: pipe.stc(subjFunctionalFormat)
if options.realign: pipe.realign(subjRealignJob)
if options.motioncheck: pipe.motionCheck(MOTION_THRESHOLD)
if options.calcderivs: pipe.calcDerivs()
if options.fmap and subjHasFmap: pipe.fieldMap()
if options.normalize: pipe.normSmooth(subjNormJob)
if options.moveLocalFiles: pipe.moveLocalFilesToNetwork()

if options.stats: 
	os.chdir(pipe.statsdir)
	pipe.stats1L(subjStatsJob)
	os.chdir(current)




