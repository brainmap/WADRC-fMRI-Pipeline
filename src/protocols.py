## Classes used to hold constants for different types of study protocols.

import os

class RiesCmsUwmr(object):
	protocolName = 'ries.cms.uwmr'
	protocolDesc = 'Micheles Hospital CMS data.'
	studyName = 'alz'
	studyPrefix = '2'
	studyFunctionalFormat = 'dicoms'
	#studyRawDir = '/Data/vtrak1/raw/cms/uwmr'
	studyRawDir = '/tmp/ries.cms.uwmr/raw'
	studyPreprocDir = os.path.join('/tmp', protocolName, 'preproc')
	studyStatsDir = os.path.join('/tmp', protocolName, 'stats')
	studyOnsetsDir = None
	studyTemplatesDir = '/Data/vtrak1/preprocessed/progs/ries.cms.uwmr/templates'

	realignJobFile = 'ries.cms.uwmr_realign.mat'
	realignTemplateSubid = 'cms_001'
	realignTemplatePreprocDir = '/tmp/ries.cms.uwmr/preproc'
	realignTemplateRuns = ['fMRI_004', 'fMRI_005']
	realignTemplateFM = False

	normJobFile = 'ries.cms.uwmr_norm.mat'
	normTemplateSubid = 'cms_001'
	normTemplatePreprocDir = '/tmp/ries.cms.uwmr/preproc'
	normTemplateRuns = ['fMRI_004', 'fMRI_005']
	normTemplateFM = False

	statsJobFile = 'ries.cms.uwmr_stats.mat'
	statsTemplateSubid = 'cms_001'
	statsTemplatePreprocDir = '/home/erik/pipeline_dev/preproc'
	statsTemplateStatsDir = '/home/erik/pipeline_dev/stats'
	statsTemplateOnsetsDir = '/home/erik/pipeline_dev/spm_templates'
	statsTemplateRuns = ['fMRI_004','fMRI_005']
	statsTemplateFM = False

	realignJob = os.path.join(studyTemplatesDir, realignJobFile)
	normJob = os.path.join(studyTemplatesDir, normJobFile)
	statsJob = os.path.join(studyTemplatesDir, statsJobFile)
	
class RiesCmsUwmrRest(RiesCmsUwmr):
	protocolName = 'ries.cms.uwmr'
	protocolDesc = 'Micheles Hospital CMS data.'
	studyFunctionalFormat = 'dicoms'
	studyRawDir = '/Data/vtrak1/raw/cms/uwmr'
	studyPreprocDir = '/Data/vtrak1/preprocessed/modalities/fmri/ries.cms.uwmr.rest'
	studyStatsDir = '/Data/vtrak1/1L_stats/glm/ries.cms.uwmr.rest'
	studyOnsetsDir = None
	studyTemplatesDir = '/Data/vtrak1/preprocessed/progs/ries.cms.uwmr/templates'
	
	realignJobFile = 'ries.cms.uwmr.rest_realign.mat'
	realignTemplateSubid = 'cms_042'
	realignTemplatePreprocDir = '/tmp/ries.cms.uwmr/preproc'
	realignTemplateRuns = ['assetRun1', 'assetRun2', 'assetRest195', 'assetRest165']
	realignTemplateFM = False

	normJobFile = 'ries.cms.uwmr.rest_norm.mat'
	normTemplateSubid = 'cms_042'
	normTemplatePreprocDir = '/tmp/ries.cms.uwmr/preproc'
	normTemplateRuns = ['assetRun1', 'assetRun2', 'assetRest195', 'assetRest165']
	normTemplateFM = False

	statsJobFile = 'ries.cms.uwmr.rest_stats.mat'
	statsTemplateSubid = 'cms_001'
	statsTemplatePreprocDir = '/tmp/ries.cms.uwmr/preproc'
	statsTemplateStatsDir = '/tmp/ries.cms.uwmr/stats'
	statsTemplateOnsetsDir = None
	statsTemplateRuns = ['fMRI_004', 'fMRI_005']
	statsTemplateFM = False
	
	realignJob = os.path.join(studyTemplatesDir, realignJobFile)
	normJob = os.path.join(studyTemplatesDir, normJobFile)
	statsJob = os.path.join(studyTemplatesDir, statsJobFile)

# WRAP-140
#class Wrap140(object):
#	protocolName = 'Johnson.Wrap140.Visit1'
#	protocolDesc = 'For Processing Wrap140 Functional and Resting Data'
#	studyRawDir = '/Data/vtrak1/raw/wrap140'
#	studyPreprocDir = '/tmp/wrap140fmri'
#	studyStatsDir = '/Data/vtrak1/1L_stats/glm/wrap140'
#	studyOnsetsDir = '/Data/vtrak1/preprocessed/progs/wrap140/onsets/'
#	studyTemplatesDir = '/Data/vtrak1/preprocessed/progs/wrap140/templates'
#
#	realignJobFile = 'wrap140_realign.mat'
#	realignTemplateSubid = '2501'
#	realignTemplatePreprocDir = '/Data/vtrak1/preprocessed/modalities/fmri/wrap140'
#	realignTemplateRuns = ['AssetRun1', 'AssetRun2']
#	realignTemplateFM = False
#
#	normJobFile = 'wrap140_norm.mat'
#	normTemplateSubid = '2501'
#	normTemplatePreprocDir = '/Data/vtrak1/preprocessed/modalities/fmri/wrap140'
#	normTemplateRuns = ['AssetRun1', 'AssetRun2']
#	normTemplateFM = True
#
#	statsJobFile = 'wrap140_stats.mat'
#	statsTemplateSubid = '2501'
#	statsTemplatePreprocDir = '/Data/vtrak1/preprocessed/modalities/fmri/wrap140'
#	statsTemplateStatsDir = '/Data/vtrak/1L_stats/glm/wrap140'
#	statsTemplateOnsetsDir = '/Data/vtrak1/1L_stats/glm/wrap140'
#	statsTemplateRuns = ['AssetRun1','AssetRun2']
#	statsTemplateFM = True
#
#	realignJob = os.path.join(studyTemplatesDir, realignJobFile)
#	normJob = os.path.join(studyTemplatesDir, normJobFile)
#	statsJob = os.path.join(studyTemplatesDir, statsJobFile)

# This AdaptRecog is for Protocols With Rest, and with 2 Timepoints (Longitudinal).
class AdaptRecogWithRest_Lon(object):
	protocolName = 'Johnson.ALZ.AdaptRecogWithRest'
	protocolDesc = 'ALZ2_AdaptRecogWithRest'
	studyName = 'alz'
	studyPrefix = '2'
	studyRawDir = '/tmp/alz2adaptrecog_test/raw/'
	studyPreprocDir = '/tmp/alz2adaptrecog_test/preproc'
	studyStatsDir = '/tmp/alz2adaptrecog_test/stats'
	studyOnsetsDir = '/tmp/alz2adaptrecog_test/progs/onsets/'
	studyTemplatesDir = '/tmp/alz2adaptrecog_test/progs/templates'

	realignJobFile = 'johnson.alz.adaptrecogwithrest_realign.mat'
	realignTemplateSubid = 'alz253_2'
	realignTemplatePreprocDir = '/tmp/alz2adaptrecog_test/preproc'
	realignTemplateRuns = ['adaptA','adaptB','adaptC','adaptD','alzrest210','alzrest165','recogA','recogB']
	realignTemplateFM = False

	normJobFile = 'johnson.alz.adaptrecogwithrest_norm.mat'
	normTemplateSubid = 'alz253_2'
	normTemplatePreprocDir = '/tmp/alz2adaptrecog_test/preproc'
	normTemplateRuns = ['adaptA','adaptB','adaptC','adaptD','alzrest210','alzrest165','recogA','recogB']
	normTemplateFM = True

	statsJobFile = 'alzVisit2_stats.mat'
	statsTemplateSubid = '2017_2'
	statsTemplatePreprocDir = '/home/erik/pipeline_dev/preproc'
	statsTemplateStatsDir = '/home/erik/pipeline_dev/stats'
	statsTemplateOnsetsDir = '/home/erik/pipeline_dev/spm_templates'
	statsTemplateRuns = ['snodC','snodD']
	statsTemplateFM = True

	realignJob = os.path.join(studyTemplatesDir, realignJobFile)
	normJob = os.path.join(studyTemplatesDir, normJobFile)
	statsJob = os.path.join(studyTemplatesDir, statsJobFile)

# This is a testing protocol for use with the Adaptation/Recognition procedure.
# Testing goes in /tmp on Miho.  (It's currently identical to the procdure
# named without testing, but that will eventually be given proper paths.
# 2/17/09 - EKK
class AdaptRecogWithRest_ekktesting(object):
	protocolName = 'Johnson.ALZ.AdaptRecogWithRest'
	protocolDesc = 'ALZ2_AdaptRecogWithRest'
	studyName = 'alz'
	studyPrefix = '2'
	studyRawDir = '/tmp/alz2adaptrecog_test/raw/'
	studyPreprocDir = '/tmp/alz2adaptrecog_test/preproc'
	studyStatsDir = '/tmp/alz2adaptrecog_test/stats'
	studyOnsetsDir = '/tmp/alz2adaptrecog_test/progs/onsets/'
	studyTemplatesDir = '/tmp/alz2adaptrecog_test/progs/templates'

	realignJobFile = 'johnson.alz.adaptrecogwithrest_realign.mat'
	realignTemplateSubid = 'alz253_2'
	realignTemplatePreprocDir = '/tmp/alz2adaptrecog_test/preproc'
	realignTemplateRuns = ['adaptA','adaptB','adaptC','adaptD','alzrest210','alzrest165','recogA','recogB']
	realignTemplateFM = False

	normJobFile = 'johnson.alz.visit2.adaptrecogwithrest_norm.mat'
	normTemplateSubid = 'alz253_2'
	normTemplatePreprocDir = '/tmp/alz2adaptrecog_test/preproc'
	normTemplateRuns = ['adaptA','adaptB','adaptC','adaptD','alzrest210','alzrest165','recogA','recogB']
	normTemplateFM = True

	statsJobFile = 'alzVisit2_stats.mat'
	statsTemplateSubid = 'alz253_2'
	statsTemplatePreprocDir = '/tmp/alz2adaptrecog_test/preproc'
	statsTemplateStatsDir = '/tmp/alz2adaptrecog_test/stats'
	statsTemplateOnsetsDir = '/tmp/alz2adapterecog_test/progs/templates'
	statsTemplateRuns = ['adaptA','adaptB','adaptC','adaptD','alzrest210','alzrest165','recogA','recogB']
	statsTemplateFM = True

	realignJob = os.path.join(studyTemplatesDir, realignJobFile)
	normJob = os.path.join(studyTemplatesDir, normJobFile)
	statsJob = os.path.join(studyTemplatesDir, statsJobFile)

# This AdaptRecog is for Protocols without Rest and longitudinal (with 2 timepoints.)
class AdaptRecog_Lon(object):
	protocolName = 'Johnson.ALZ.AdaptRecog'
	protocolDesc = 'AdaptRecog'
	studyName = 'alz'
	studyPrefix = '2'
	studyRawDir = '/tmp/alz2adaptrecog_test/raw/'
	studyPreprocDir = '/tmp/alz2adaptrecog_test/preproc'
	studyStatsDir = '/tmp/alz2adaptrecog_test/stats'
	studyOnsetsDir = '/tmp/alz2adaptrecog_test/progs/onsets/'
	studyTemplatesDir = '/tmp/alz2adaptrecog_test/progs/templates'

	realignJobFile = 'johnson.alz.adaptrecog_realign.mat'
	realignTemplateSubid = 'alz253_2'
	realignTemplatePreprocDir = '/tmp/alz2adaptrecog_test/preproc'
	realignTemplateRuns = ['adaptA','adaptB','adaptC','adaptD','recogA','recogB']
	realignTemplateFM = False

	normJobFile = 'johnson.alz.adaptrecog_norm.mat'
	normTemplateSubid = 'alz253_2'
	normTemplatePreprocDir = '/tmp/alz2adaptrecog_test/preproc'
	normTemplateRuns = ['adaptA','adaptB','adaptC','adaptD','recogA','recogB']
	normTemplateFM = True

	statsJobFile = None
	statsTemplateSubid =  None
	statsTemplatePreprocDir =  None
	statsTemplateStatsDir =  None
	statsTemplateOnsetsDir =  None
	statsTemplateRuns =  None
	statsTemplateFM =  None

	realignJob = os.path.join(studyTemplatesDir, realignJobFile)
	normJob = os.path.join(studyTemplatesDir, normJobFile)
	statsJob = None

# This AdaptRecog is for Protocols without Rest and for a single timepoint.
class AdaptRecog(object):
	protocolName = 'Johnson.ALZ.AdaptRecog'
	protocolDesc = 'AdaptRecog (Without Rest, Single Timepoint)'
	studyName = 'alz'
	studyPrefix = '2'
	studyRawDir = '/Data/vtrak1/raw/alz_2000'
	studyPreprocDir = '/Data/vtrak1/preprocessed/modalities/fmri/johnson.alz.visit1.AdaptRecog'
	studyStatsDir = '/Data/vtrak1/1L_stats/glm/johnson.alz.visit1.Adapt'
	studyOnsetsDir = None
	studyTemplatesDir = '/Data/vtrak1/preprocessed/progs/johnson.alz.visit1.AdaptRecog/templates'

	realignJobFile = 'johnson.alz.adaptrecog_realign.mat'
	realignTemplateSubid = 'alz253_2'
	realignTemplatePreprocDir = '/tmp/alz2adaptrecog_test/preproc'
	realignTemplateRuns = ['adaptA','adaptB','adaptC','adaptD','recogA','recogB']
	realignTemplateFM = False

	normJobFile = 'johnson.alz.adaptrecog_norm.mat'
	normTemplateSubid = 'alz246_2'
	normTemplatePreprocDir = '/tmp/alz2adaptrecog_test/preproc'
	normTemplateRuns = ['adaptA','adaptB','adaptC','adaptD','recogA','recogB']
	normTemplateFM = True

	statsJobFile = 'johnson.alz.adaptrecog_stats.mat'
	statsTemplateSubid =  'alz001_2'
	statsTemplatePreprocDir = '/Data/vtrak1/preprocessed/modalities/fmri/johnson.alz.visit1.AdaptRecog'
	statsTemplateStatsDir =  '/Data/vtraks1/1L_stats/glm/johnson.alz.visit1.Adapt'
	statsTemplateOnsetsDir =  None
	statsTemplateRuns =  ['adaptB','adaptA','adaptD','adaptC','recogA','recogB']
	statsTemplateFM =  True

	realignJob = os.path.join(studyTemplatesDir, realignJobFile)
	normJob = os.path.join(studyTemplatesDir, normJobFile)
	statsJob = os.path.join(studyTemplatesDir, statsJobFile)

class AdaptRecog_ekk(AdaptRecog):
	studyPreprocDir = '/tmp/alz2adaptrecog_test/preproc'
	studyStatsDir = '/tmp/alz2adaptrecog_test/stats'
    
class ALZ2_final(object):
	protocolName = 'alzVisit2'
	protocolDesc = '2nd Visit ALZ Follow-Up - 2XSnod + 1 210 Rep Resting Bold'
	studyName = 'alz'
	studyPrefix = '2'
	studyRawDir = '/Data/vtrak1/raw/alz_2000'
	studyPreprocDir = '/Data/vtrak1/preprocessed/modalities/fmri/alzVisit2'
	studyStatsDir = '/Data/vtrak1/1L_stats/glm/alzVisit2'
	studyOnsetsDir = '/Data/vtrak1/preprocessed/progs/alzVisit2'
	studyTemplatesDir = '/Data/vtrak1/preprocessed/progs/alzVisit2'
	
	realignJobFile = 'alzVisit2_realign.mat'
	realignTemplateSubid = '2017_2'
	realignTemplatePreprocDir = '/home/erik/pipeline_dev/preproc'
	realignTemplateRuns = ['snodC','snodD','rest120']
	realignTemplateFM = False
	
	normJobFile = 'alzVisit2_norm.mat'
	normTemplateSubid = '2017_2'
	normTemplatePreprocDir = '/home/erik/pipeline_dev/preproc'
	normTemplateRuns = ['snodC','snodD','rest120']
	normTemplateFM = True
	
	statsJobFile = 'alzVisit2_stats.mat'
	statsTemplateSubid = '2017_2'
	statsTemplatePreprocDir = '/home/erik/pipeline_dev/preproc'
	statsTemplateStatsDir = '/home/erik/pipeline_dev/stats'
	statsTemplateOnsetsDir = '/home/erik/pipeline_dev/spm_templates'
	statsTemplateRuns = ['snodC','snodD']
	statsTemplateFM = True
	
	realignJob = os.path.join(studyTemplatesDir, realignJobFile)
	normJob = os.path.join(studyTemplatesDir, normJobFile)
	statsJob = os.path.join(studyTemplatesDir, statsJobFile)

class ALZ2_testing(ALZ2_final):
	# not a real protocol, used for test / retest of pipeline output
	protocolName = 'alzVisit2'
	protocolDesc = '2nd Visit ALZ Follow-Up - 2XSnod + 1 210 Rep Resting Bold'
	studyName = 'alz'
	studyPrefix = '2'
	studyRawDir = '/Data/vtrak1/test/alz2/raw'
	studyPreprocDir = '/Data/vtrak1/test/alz2/preproc'
	studyStatsDir = '/Data/vtrak1/test/alz2/stats'
	studyOnsetsDir = '/Data/vtrak1/preprocessed/progs/alzVisit2'
	studyTemplatesDir = '/Data/vtrak1/preprocessed/progs/alzVisit2'


class ALZ2_kjktest(ALZ2_final):
	# not a real protocol, used for kjk's personal testing directories
	protocolName = 'alzVisit2'
	protocolDesc = '2nd Visit ALZ Follow-Up - 2XSnod + 1 210 Rep Resting Bold'
	studyName = 'alz'
	studyPrefix = '2'
	studyRawDir = '/home/kris/pipeline_dev/test_subject/raw'
	studyPreprocDir = '/home/kris/pipeline_dev/test_subject/preproc'
	studyStatsDir = '/home/kris/pipeline_dev/test_subject/stats'
	studyOnsetsDir = '/home/kris/pipeline_dev/test_subject/onsets'
	studyTemplatesDir = '/home/kris/pipeline_dev/test_subject/jobs'

class ALZ1_test(object):
	protocolName = 'alzVisit1'
	protocolDesc = '1st Visit ALZ - 2XSnod + 2X Self/Word'
	studyName = 'alz'
	studyPrefix = '2'
	studyRawDir = '/Data/vtrak1/raw/alz_2000'
	studyPreprocDir = '/Data/vtrak1/preprocessed/modalities/fmri/alzVisit1'
	studyStatsDir = '/Data/vtrak1/1L_stats/glm/alzVisit1'
	studyOnsetsDir = '/Data/vtrak1/preprocessed/progs/alzVisit1'
	studyTemplatesDir = '/Data/vtrak1/preprocessed/progs/alzVisit1'
	
	realignJobFile = 'alzVisit1_realign.mat'
	realignTemplateSubid = '2021'
	realignTemplatePreprocDir = '/Data/vtrak1/preprocessed/modalities/fmri/alzVisit1'
	realignTemplateRuns = ['swA','swB','snodD','snodC']
	realignTemplateFM = False
	
	normJobFile = 'alzVisit1_norm.mat'
	normTemplateSubid = '2021'
	normTemplatePreprocDir = '/Data/vtrak1/preprocessed/modalities/fmri/alzVisit1'
	normTemplateRuns = ['swA','swB','snodD','snodC']
	normTemplateFM = True
	
	statsJobFile = 'alzVisit1_stats.mat'
	statsTemplateSubid = '2017_2'
	statsTemplatePreprocDir = '/Data/vtrak1/preprocessed/modalities/fmri/alzVisit1'
	statsTemplateStatsDir = '/Data/vtrak1/1Lstats/glm/alzVisit1'
	statsTemplateOnsetsDir = '/Data/vtrak1/preprocessed/progs/alzVisit1'
	statsTemplateRuns = ['snodC','snodD']
	statsTemplateFM = True
	
	realignJob = os.path.join(studyTemplatesDir, realignJobFile)
	normJob = os.path.join(studyTemplatesDir, normJobFile)
	statsJob = os.path.join(studyTemplatesDir, statsJobFile)
