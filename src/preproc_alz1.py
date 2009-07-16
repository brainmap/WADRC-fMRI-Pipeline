#!/usr/bin/env python
"""Preprocess a subject in the alz visit 1 protocol.

preproc_alz1.py <subject ID> [pipe options]
"""

import sys, os, shutil
sys.path.append('/home/kris/pipeline_dev/ken_trunk/python_pipeline/trunk')
sys.path.append('/Data/vtrak1/SysAdmin/production/python')
from optparse import OptionParser
from greccparsers import subject_parse
from spmjobs import *
from pipeline import Pipeline
from protocols import ALZ1_test as ALZ1

SUBJECT_INFO_CSV = '/Data/vtrak1/preprocessed/progs/alzVisit1/subject_run_info.csv'
MOTION_THRESHOLD = 1

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
parser.add_option("-x","--stats",action="store_true",dest="stats",
    default=False, help="run first level stats")
parser.add_option("--freshstart",action="store_true",dest="fresh",
    default=False, help="removes preproc and stats directories, starts fresh.")
(options, args) = parser.parse_args()

if (len(args) != 1):
    parser.error("Incorrect number of arguments, subject ID missing.")
subid = args[0]

# retrieves a dictionary of subject specific visit variables from the csv file
subjVisitVars = subject_parse(SUBJECT_INFO_CSV, str(subid))
subjHasFmap = bool(subjVisitVars['hasfmap'][0])
subjTasks = subjVisitVars['tasks']
subjPfiles = subjVisitVars['pfiles']

subjRawDir = os.path.join(ALZ1.studyRawDir, subid, 'raw')
subjAnatDir = os.path.join(subjRawDir, 'anatomicals')
subjPreprocDir = os.path.join(ALZ1.studyPreprocDir, subid)
subjStatsDir = os.path.join(ALZ1.studyStatsDir, subid)
subjRealignJob = os.path.join(subjPreprocDir, subid+'_realign.mat')
subjNormJob = os.path.join(subjPreprocDir, subid+'_norm.mat')
subjStatsJob = os.path.join(subjPreprocDir, subid+'_stats.mat')
#statstasks = filter(lambda x: x.startswith('snod'), subjVisitVars['tasks'])
statstasks = [ task for task in subjVisitVars['tasks'] if task.startswith('snod') ]

print """
##########################################################
#                                                        #
#    Welcome to the ALZ Visit 1 preprocessing script     #
#                                                        #
##########################################################
"""

varstoprint = dict(subid=subid,subjRawDir=subjRawDir,subjAnatDir=subjAnatDir,subjPreprocDir=subjPreprocDir,
    subjStatsDir=subjStatsDir,subjRealignJob=subjRealignJob,subjNormJob=subjNormJob,
    subjStatsJob=subjStatsJob,statstasks=statstasks,subjTasks=subjTasks,subjPfiles=subjPfiles)
fstr = "%-30s : %s"
for key,val in varstoprint.items():
    print fstr % (key,val)

if options.fresh:
    if os.path.exists(subjPreprocDir): shutil.rmtree(subjPreprocDir)
    if os.path.exists(subjStatsDir): shutil.rmtree(subjStatsDir)
    for option in options.__dict__:
    	options.__dict__[option] = True

if not os.path.exists(subjPreprocDir):
    os.mkdir(subjPreprocDir)
    os.mkdir(subjStatsDir)
    shutil.copy(ALZ1.realignJob, subjRealignJob)
    shutil.copy(ALZ1.normJob, subjNormJob)
    shutil.copy(ALZ1.statsJob, subjStatsJob)
    
    # subject's identity for realignment and normalization
    subj_identity = SPMJobIdentity (
        subid,
        [ALZ1.studyPreprocDir],
        subjVisitVars['tasks'],
        fieldmap= subjHasFmap and options.fmap
    )

    # making a job instance for the template realign job and changing its identity
    realign_template_identity = SPMJobIdentity (
        ALZ1.realignTemplateSubid,
        [ALZ1.realignTemplatePreprocDir],
        ALZ1.realignTemplateRuns,
        fieldmap=ALZ1.realignTemplateFM
    )
    realign_job = SPMJob(subjRealignJob, realign_template_identity)
    realign_job.replaceIdentity(subj_identity)

    # make and change norm job instance
    norm_template_identity = SPMJobIdentity(
        ALZ1.normTemplateSubid,
        [ALZ1.normTemplatePreprocDir],
        ALZ1.normTemplateRuns,
        fieldmap=ALZ1.normTemplateFM
    )
    norm_job = SPMJob(subjNormJob, norm_template_identity)
    norm_job.replaceIdentity(subj_identity)


    # subject's identity for stats job, need to exclude rest 120 for stats
    subj_stats_identity = SPMJobIdentity (
        subid,
        [ALZ1.studyPreprocDir, ALZ1.studyStatsDir, ALZ1.studyOnsetsDir],
        statstasks,
        fieldmap= subjHasFmap and options.fmap
    )

    # make and change stats job instance
    stats_template_identity = SPMJobIdentity (
        ALZ1.statsTemplateSubid,
        [ALZ1.statsTemplatePreprocDir, ALZ1.statsTemplateStatsDir, ALZ1.statsTemplateOnsetsDir],
        ALZ1.statsTemplateRuns,
        fieldmap=ALZ1.statsTemplateFM
    )
    stats_job = SPMJob(subjStatsJob, stats_template_identity)
    stats_job.replaceIdentity(subj_stats_identity)





# make a pipe, run it.
pipe = Pipeline(subid, subjRawDir, subjAnatDir, subjPreprocDir, subjStatsDir)
pipe.checkSetup()
if options.recon: pipe.recon(subjVisitVars['tasks'], subjVisitVars['pfiles'], ALZ1.studyName)
if options.stc: pipe.stc()
if options.realign: pipe.realign(subjRealignJob)
if options.motioncheck: pipe.motionCheck(MOTION_THRESHOLD)
if options.calcderivs: pipe.calcDerivs()
if subjHasFmap and options.fmap: pipe.fieldMap()
if options.normalize: pipe.normSmooth(subjNormJob)
if options.stats: pipe.stats1L(subjStatsJob)






