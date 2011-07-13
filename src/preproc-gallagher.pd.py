#!/usr/bin/env python
import os
from subprocess import *
os.environ["FSLOUTPUTTYPE"]="NIFTI"

class StudyVariables(object):
################### USERS EDIT THE VARIABLES BELOW##############################
################### TO ADAPT THEM TO YOUR OWN PROJECT. #########################
    protocolName = 'gallagher.pd'
    protocolDesc = 'Gallagher.pd with 195/165 Rest'
    studyName = None
    studyPrefix = 'pd'
    studyFunctionalFormat = 'dicoms'
    studyRawDir = '/Data/vtrak1/raw/gallagher.pd/mri'
    studyPreprocDir = '/Data/vtrak1/preprocessed/visits/gallagher.pd'
    studyStatsDir = '/Data/vtrak1/preprocessed/visits/gallagher.pd'
    studyOnsetsDir = None
    studyTemplatesDir = '/Data/vtrak1/preprocessed/progs/gallagher.pd/EqualLengthRestTemplates'

    realignJobFile = 'gallagher.pd_realign.mat'
    realignTemplateSubid = '2501'
    realignTemplatePreprocDir = '/Data/tmp/2501'
    realignTemplateRuns = []
    realignTemplateFM = False

    normJobFile = 'gallagher.pd_norm.mat'
    normTemplateSubid = '2501'
    normTemplatePreprocDir = '/Data/tmp/2501'
    normTemplateRuns = []
    normTemplateFM = False

    # statsJobFile = 'gallagher.pd_stats.mat'
    # statsTemplateSubid = 'wrp001'
    # statsTemplatePreprocDir = '/Data/vtrak1/preprocessed/visits/wrap140.visit1'
    # statsTemplateStatsDir = '/Data/vtrak1/preprocessed/visits/wrap140.visit1'
    # statsTemplateOnsetsDir = None
    # statsTemplateRuns = []
    # statsTemplateFM = False
    # subjectInfoCSV = None

    realignJob = os.path.join(studyTemplatesDir, realignJobFile)
    normJob = os.path.join(studyTemplatesDir, normJobFile)
    statsJob = None # os.path.join(studyTemplatesDir, statsJobFile)
######################### DO NOT EDIT BELOW THIS LINE #########################
############################# ON PAIN OF DEATH ################################
############################### WE'RE NOT KIDDING #############################


"""Preprocess a subject for WRAP 140 First Visit
preproc-wrap140.visit1.py <subject ID> [pipe options]
"""

import sys
import shutil
import glob
# sys.path.append('/Data/home/erik/NetBeansProjects/PythonPipeline/src')
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
    parser.add_option("--working-dir",dest="workingdir",help="Temporary local working directory.",metavar="DIR")
    return parser

(options, args) = makeOptionsParser().parse_args()

if (len(args) != 1):
    parser.error("Incorrect number of arguments, subject ID missing.")
subid = args[0]


# retrieves a dictionary of subject specific visit variables from the csv file
subjHasFmap = False
subjFunctionalFormat = StudyVariables.studyFunctionalFormat

# Subject Variable Defaults from Hospital:
subjRawDir = glob.glob(os.path.join(StudyVariables.studyRawDir, subid + '*'))[0]
subjAnatDir = subjRawDir
subjPreprocDir = os.path.join(StudyVariables.studyPreprocDir, subid, 'fmri')
subjStatsDir = None # os.path.join(StudyVariables.studyStatsDir, subid, 'stats_basic')
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
    # if os.path.exists(subjStatsDir): shutil.rmtree(subjStatsDir)

if options.all:
    for option in options.__dict__: options.__dict__[option] = True
    options.stats = False

# Check Write Permissions in Subject Paths
# for path in [subjPreprocDir, subjStatsDir]:
for path in [subjPreprocDir]:
    if os.path.exists(path):
        if not os.access(path, os.W_OK): raise IOError("Cannot Write to Subject Directory " + path)
    else: os.makedirs(path)


# make a pipe, run it.
pipe = Pipeline(subid, subjRawDir, subjAnatDir, subjPreprocDir, subjStatsDir, options.workingdir)
pipe.checkSetup()

subjRealignJob = os.path.join(pipe.working_preprocdir, subid+'_realign.mat')
subjNormJob = os.path.join(pipe.working_preprocdir, subid + '_norm.mat')
# subjStatsJob = os.path.join(subjStatsDir, subid + '_stats.mat')

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
    ('subjPreprocDir',subjPreprocDir),('subjStatsDir',subjStatsDir),('StudyVariables.studyName',StudyVariables.studyName),
    ('MOTION_THRESHOLD',MOTION_THRESHOLD)
]:
    print "%-30s : %s" % nameValue



# Subject customization occurs only by including subid; otherwise paths do not
# contain subject information.
#
# The path to the working directory (the first half of what is returned from split)
# replaces the subject template directory.
print pipe.working_preprocdir
# subject's identity for realignment and normalization
subj_preproc_identity = SPMJobIdentity (
    subid,
    [pipe.working_preprocdir ],
    statstasks,
    fieldmap= subjHasFmap and options.fmap
)

# subject's identity for stats
# subj_stats_identity = SPMJobIdentity (
#     subid,
#     [StudyVariables.studyPreprocDir, StudyVariables.studyStatsDir, StudyVariables.studyOnsetsDir],
#     statstasks,
#     fieldmap= subjHasFmap and options.fmap
# )


current = os.getcwd()
os.chdir(pipe.working_preprocdir)
if options.recon: 
    pipe.recon(StudyVariables.studyName, subjFunctionalFormat)
    # if os.path.exists(subid + '_assetRun1.nii'): pipe.remove_discdacqs(subid + '_assetRun1.nii', 2)
    # if os.path.exists(subid + '_assetRun2.nii'): pipe.remove_discdacqs(subid + '_assetRun2.nii', 2)
    if os.path.exists(subid + '_assetRest195.nii'): pipe.remove_discdacqs(subid + '_assetRest195.nii', 32)
    if os.path.exists(subid + '_assetRest165.nii'): pipe.remove_discdacqs(subid + '_assetRest165.nii', 2)
    
if options.stc: pipe.stc(subjFunctionalFormat)
if options.realign:
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

    pipe.realign(subjRealignJob)

if options.motioncheck: pipe.motionCheck(MOTION_THRESHOLD)
if options.calcderivs: pipe.calcDerivs()
if options.fmap and subjHasFmap: pipe.fieldMap()
if options.normalize: 
    print 'Subject Norm Job:'
    print subjNormJob
    if subjNormJob:     print "%-30s : %s" % ('subjNormJob',subjNormJob)
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

    pipe.normSmooth(subjNormJob)

if options.moveLocalFiles: pipe.moveLocalFilesToNetwork()
if options.stats: 
    os.chdir(pipe.statsdir)
    if subjStatsJob:    print "%-30s : %s" % ('subjStatsJob',subjStatsJob)
    if statstasks:  print "%-30s : %s" % ('statstasks',statstasks)
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

    pipe.stats1L(subjStatsJob)

os.chdir(current)

