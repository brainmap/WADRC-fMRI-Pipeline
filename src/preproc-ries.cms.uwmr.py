#!/usr/bin/env python
"""Preprocess a subject in the alz visit 2 protocol.

preproc_alz2.py <subject ID> [pipe options]
"""

import sys
import os
import shutil
sys.path.append('/Data/home/erik/NetBeansProjects/PythonPipeline/src')
sys.path.append('/Data/vtrak1/SysAdmin/production/python')
from optparse import OptionParser
from greccparsers import subject_parse
from spmjobs import *
from pipeline import Pipeline


SUBJECT_INFO_CSV = '/Data/vtrak1/preprocessed/progs/ries.cms.uwmr/cms_subjects.csv'
MOTION_THRESHOLD = 1

def makeOptionsParser():
	# Argument/options parsing
	parser = OptionParser( usage = __doc__ )
	parser.add_option("-r","--recon",action="store_true",dest="recon",
	    default=False, help="reconstruct images from raw")
	parser.add_option("-s","--stc",action="store_true",dest="stc",
	    default=False, help="slice time correct images")
	parser.add_option("-a","--realign",action="store_true",dest="realign",
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
	parser.add_option("--wrapper",default="RiesCmsUwmrRest")
	parser.add_option("--all",action="store_true",dest="all",
		default=False, help="Run Recon, stc, realign, motioncheck, calcderiv, fieldmap, norm, move files and stats.")
	return parser

(options, args) = makeOptionsParser().parse_args()

if (len(args) != 1):
    parser.error("Incorrect number of arguments, subject ID missing.")
subid = args[0]


exec("from protocols import %s as StudyVariables" % (options.wrapper, ))


# retrieves a dictionary of subject specific visit variables from the csv file
subjVisitVars = subject_parse(SUBJECT_INFO_CSV, str(subid))
subjHasFmap = bool(subjVisitVars['hasfmap'][0])
subjTasks = subjVisitVars['tasks']
subjPfiles = subjVisitVars['pfiles']
subjHasFmap = None
subjFunctionalFormat = StudyVariables.studyFunctionalFormat

# Subject Variable Defaults from Hospital:
subjRawDir = os.path.join(StudyVariables.studyRawDir, subid)
subjAnatDir = os.path.join(subjRawDir)
subjPreprocDir = os.path.join(StudyVariables.studyPreprocDir, subid)
subjStatsDir = os.path.join(StudyVariables.studyStatsDir, subid)
subjLonDir = os.path.join(subjPreprocDir, 'lon')
#statstasks = filter(lambda x: x.startswith('snod'), subjVisitVars['tasks'])
statstasks = [ task for task in subjVisitVars['tasks'][0:2]]

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


varstoprint = dict(subid=subid,subjRawDir=subjRawDir,subjAnatDir=subjAnatDir,subjPreprocDir=subjPreprocDir,
    subjStatsDir=subjStatsDir,subjRealignJob=subjRealignJob,subjNormJob=subjNormJob,
    subjStatsJob=subjStatsJob)
#statstasks=statstasks,subjTasks=subjTasks,subjPfiles=subjPfiles

fstr = "%-30s : %s"
for key,val in varstoprint.items():
    print fstr % (key,val)



str = "%-30s : %s"
print str % ('subid',subid)
print str % ('subjRawDir',subjRawDir)
print str % ('subjAnatDir',subjAnatDir)
print str % ('subjPreprocDir',subjPreprocDir)
print str % ('subjStatsDir',subjStatsDir)
print str % ("subjVisitVars['tasks']",subjVisitVars['tasks'])
print str % ("subjVisitVars['pfiles']",subjVisitVars['pfiles'])
if subjVisitVars.has_key('refdat_files'): print str % ("subjVisitVars['refdat_files']",subjVisitVars['refdat_files'])
print str % ("subjVisitVars['hasfmap'][0]",subjVisitVars['hasfmap'][0])
print str % ("options.fmap",options.fmap)
if subjHasFmap: print str % ("do fmap?", subjHasFmap and options.fmap)
print str % ('ALZ2.studyName',StudyVariables.studyName)
print str % ('subjRealignJob',subjRealignJob)
print str % ('MOTION_THRESHOLD',MOTION_THRESHOLD)
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
    subjVisitVars['tasks'],
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
if options.recon: pipe.recon(StudyVariables.studyName, subjFunctionalFormat)
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




