#!/usr/bin/env python
import os

class StudyVariables(object):
################### USERS EDIT THE VARIABLES BELOW##############################
################### TO ADAPT THEM TO YOUR OWN PROJECT. #########################
	protocolName = 'ries.aware.visit1'
	protocolDesc = 'Micheles anosognosia Aware R01.'
	studyName = None
	studyPrefix = 'awr'
	studyFunctionalFormat = 'dicoms'
	studyRawDir = '/Data/vtrak1/raw/ries.aware.visit1'
	studyPreprocDir = '/Data/vtrak1/preprocessed/visits/ries.aware.visit1'
	studyStatsDir = '/Data/vtrak1/preprocessed/visits/ries.aware.visit1'
	studyOnsetsDir = None
	studyTemplatesDir = '/Data/vtrak1/preprocessed/progs/ries.aware.visit1/templates'

	realignJobFile = 'ries.aware.visit1_realign.mat'
	realignTemplateSubid = 'awr005'
	realignTemplatePreprocDir = '/Data/tmp'
	realignTemplateRuns = []
	realignTemplateFM = False

	normJobFile = 'ries.aware.visit1_norm.mat'
	normTemplateSubid = 'awr005'
	normTemplatePreprocDir = '/Data/tmp'
	normTemplateRuns = []
	normTemplateFM = False

	statsJobFile = 'ries.aware.visit1_stats.mat'
	statsTemplateSubid = 'awr005'
	statsTemplatePreprocDir = '/Data/vtrak1/preprocessed/visits/ries.aware.visit1'
	statsTemplateStatsDir = '/Data/vtrak1/preprocessed/visits/ries.aware.visit1'
	statsTemplateOnsetsDir = None
	statsTemplateRuns = []
	statsTemplateFM = False
	subjectInfoCSV = None

	realignJob = os.path.join(studyTemplatesDir, realignJobFile)
	normJob = os.path.join(studyTemplatesDir, normJobFile)
	statsJob = os.path.join(studyTemplatesDir, statsJobFile)
######################### DO NOT EDIT BELOW THIS LINE #########################






"""Preprocess a subject for Michele Ries' Aware R01

preproc-ries.aware.visit1.py <subject ID> [pipe options]
"""

import sys
import shutil
import glob
sys.path.append('/Data/home/erik/NetBeansProjects/PythonPipeline/src')
sys.path.append('/Data/vtrak1/SysAdmin/production/python')
from optparse import OptionParser
#from greccparsers import subject_parse
from spmjobs import *
from pipeline import Pipeline


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

# Arguments for Debugging
if (len(sys.argv) == 1):
	args = ["awr019", "--all", "--freshstart"]
else: args = sys.argv

(options, args) = makeOptionsParser().parse_args(args)
print args
if (len(args) != 2):
    parser.error("Incorrect number of arguments, subject ID missing.")
subid = args[1]


# retrieves a dictionary of subject specific visit variables from the csv file
subjHasFmap = False
subjFunctionalFormat = StudyVariables.studyFunctionalFormat

# Subject Variable Defaults from Hospital:
subjRawDir = glob.glob(os.path.join(StudyVariables.studyRawDir, subid + '*'))[0]
subjAnatDir = subjRawDir
subjPreprocDir = os.path.join(StudyVariables.studyPreprocDir, subid, 'fmri')
subjStatsDir = os.path.join(StudyVariables.studyStatsDir, subid, 'stats')
subjLonDir = os.path.join(subjPreprocDir, 'lon')
statstasks = []

print """
##########################################################
#                                                        #
#    Welcome to the Preprocessing Wrapper script         #
#                                                        #
##########################################################
"""

if options.fresh:
    if os.path.exists(subjPreprocDir): shutil.rmtree(subjPreprocDir)
    if os.path.exists(subjStatsDir): shutil.rmtree(subjStatsDir)

if options.all:
    for option in options.__dict__: options.__dict__[option] = True

# Check Write Permissions in Subject Paths
for path in [subjPreprocDir, subjStatsDir]:
	if os.path.exists(path):
		if not os.access(path, os.W_OK): raise "Cannot Write to Subject Directory " + path
	else: os.makedirs(path)


# make a pipe, run it.
pipe = Pipeline(subid, subjRawDir, subjAnatDir, subjPreprocDir, subjStatsDir)
pipe.checkSetup()

subjRealignJob = os.path.join(pipe.working_preprocdir, subid+'_realign.mat')
subjNormJob = os.path.join(pipe.working_preprocdir, subid + '_norm.mat')
subjStatsJob = os.path.join(subjStatsDir, subid + '_stats.mat')
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
	('subjPreprocDir',subjPreprocDir),('subjStatsDir',subjStatsDir),('ALZ2.studyName',StudyVariables.studyName),
	('subjRealignJob',subjRealignJob),('MOTION_THRESHOLD',MOTION_THRESHOLD)
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

print subjRealignJob, StudyVariables.realignJob
if not os.path.exists(subjRealignJob) and StudyVariables.realignJob:
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


if not os.path.exists(subjNormJob) and StudyVariables.normJob:
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


if not os.path.exists(subjStatsJob) and StudyVariables.statsJob:
    shutil.copy(StudyVariables.statsJob, subjStatsJob)

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
    pipe.recon(StudyVariables.studyName, subjFunctionalFormat)
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

os.chdir(pipe.statsdir)
if options.stats: pipe.stats1L(subjStatsJob)
os.chdir(current)




