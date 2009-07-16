#!/usr/bin/env python

from optparse import OptionParser
import os, sys, re
from runcommands import run


## Used in finding modality and anat_type.
series_types = {
    "Head|Local|3pl loc": ('3PlaneLoc', None),
    "T1W|axT13d"        : ('T1', None),
    "3D IR.*T1"         : ('T1', None), 	# Sag or Cor 		#Hospital EFGRE3D
    "MP-RAGE"           : ('MPRAGE', None),
    "SagXETA-T2FLAIR"	: ("T2FlairXeta", None),
    "Sag T2-xeta"	: ("T2Xeta", None),
    " FSE|FRFSE" 	: ("T2FSE; anat_type=fse"),
    "T2.*xeta|xeta.*T2"	: ("T2Xeta", "anat_type=fse"),
    "Meas"       	: ("T2Relax", "anat_type=epan"),
    "dti|DTI"   	: ("DTI", "anat_type=epan",),
    "Flair"	        : ("T2Flair", "anat_type=fse"),
    "FLAIR"	   	: ("T2FlairXeta", "anat_type=fse"),
    "axT1 Flair"	: ("T1Flair", None),
    "Map"		: ("Fieldmap", None),
    "MT"		: ("MT", None),
    "fMRI"         	: ("fMRI", None),
    "pcASL"		: ("pcASL_flowmap", None),
    "ASL CBF"		: ("AlsopsASL", None),
    "Test"		: ("EPITest", None),
    "AxDWI"	        : ("DiffusionWeighted", None),
    "ASSET cal"		: ("ASSET_Calibration", None),
    "fMRI ASSET"	: ("fMRI_ASSET", "anat_type=epan"),
}
## Conversion of flowmap_make.sh
def flowmap_make(input_dir, num_of_images):
    orig_dir = os.getcwd()
    os.chdir(input_dir)
    series = os.path.basename(os.getcwd())
    os.system('to3d -prefix zt%s -fse -time:zt %s 2 1000 seq+z *' % (series, num_of_images)
    os.system('3df_pcasl -nex 3 -odata zt%s' % (series, )
    os.system('3dAutomask -prefix pcASL_mask.nii zt%s+orig.[1]' % (series, )
    os.system(cmd)
    os.system("3dcalc -a zt%s_fmap+orig.[0] -b pcASL_mask.nii -c zt%s+orig.[0] -expr 'a*b+c*step(1-b)' -prefix ASL_%s_flowmap.nii" % (series, series, series)
    os.system(cmd)
    os.system("3dcalc -a zt%s+orig.[1] -expr 'a' -prefix PD.nii" % (series, )
    os.system("rm zt*+orig*")
    os.chdir(orig_dir)

## Conversion of rdallhdr.sh
def rdallhdr(file):
    if re.search("I\.", file): readheader = 'rdgehdr'
    elif re.search("\.O", file): readheader = 'dicom_hdr'
    elif re.search("P", file):  readheader = 'rdgehdr'
    elif re.search("I.*\.dcm", file): readheader='dicom_hdr'
    else: readheader = "File_Type_Not_Recognized " + file
    cmd = "%s %s" % (readheader, file)
    return run(cmd)[0]

def do_recon(input, output, prefix, recon_type):
    # Check for required options.
    if None in [input, output, prefix]:
        print "You must specify an input and an output directory, and an output prefix."
        parser.print_help()
        sys.exit(1)

    # Check for recon type, set to default if necessary.
    if recon_type == None:
        recon_type = ['anat', 'fmri']
    else:
        recon_type = recon_type.split()

    # Check for presence of directories
    if not os.path.isdir(input):
        print "Specified input option must be a directory."
        parser.print_help()
        sys.exit(1)

    exclude = re.compile("(\.(img|nii|yaml|txt)$)")
    file = [f for f in os.listdir(input) if not exclude.search(f)][0]

    print "RDALL IS ", rdallhdr("%s/%s" % (input, file))
    modality, anat_type = None, None
    for pattern, results in series_types.items():
        if re.search(pattern, file):
            modality, anat_type = results
            break

    format = 'nii'
    outfile = '%s_%s.%s' % (prefix, modality, format)

    if 'anat' in recon_type:
        if modality in ['MPRAGE', 'T1', 'T1Flair', 'T2FSE', 'T2Xeta', 'T2Flair', 'T2FlairXeta']:
            atype = 'anat'
            os.environ['AFNI_SLICE_SPACING_IS_GAP']="NO"
            cmd = "to3d -session %s -prefix %s -%s %s/%s" % (output_dir, outfile, anat_type, input_dir, dcmglob)
            os.system(cmd)
        elif modality == 'pcASL_flowmap':
            atype = 'pcASL'
            number_of_pcasl_images=40 	# This is static now.  Might change?
            # flowmap_make requires cd'ing into directory, so we accommodate it here.
            flowmap_make(input_dir, number_of_pcasl_images)

            # Cleanup.
            os.system("pushd %s; mv ASL*flowmap.nii %s; mv pcASL_mask.nii %s_pcASL_mask.nii; mv PD.nii %s_PD.nii; popd" % (input_dir, outfile, prefix, prefix))
        else:
            raise "Unknown modality: " + modality

    if 'fmri' in recon_type:
        if modality == "fMRI":
            s = series_description
            if "fMRI ASSET RUN 1" in s: prefix = prefix + "_assetRun1"
            elif "fMRI ASSET RUN 2" in s: prefix = prefix + "_assetRun2"
            elif "fMRI ASSET REST 1" in s: prefix = prefix + "_assetRest195"
            elif "fMRI ASSET REST 2" in s: prefix = prefix + "_assetRest165"
            dicom_files = [f for f in os.listdir(input_dir) if f.endswith(".dcm")]
            file_count = len(dicom_files)
            if file_count > 0:
                skip = 1
                slices = [line for line in rdallhdr(os.path.join(input_dir, firstfile)) if "Images in Acquisition" in line][0].split("//")[3]
                repetition_time = [line for line in rdallhdr(os.path.join(input_dir, firstfile)) if "Repetition Time" in line][0].split("//")[3]
                bold_reps = [line for line in rdallhdr(os.path.join(input_dir, firstfile)) if "Number of Temporal Positions" in line][0].split("//")[3]
                outfile = prefix

                if os.path.exists("%s/%s.%s" % (output_dir, outfile, format)):
                    print "Series already reconstructed."
                    return
                elif os.path.exists("%s/%s+orig.BRIK.gz"):
                    run("gunzip %s/%s+orig.[BH].gz" % (output_dir, outfile))
                    skipToBrik = True
                if not skipToBrik:
                    cmd="to3d -session %(output_dir)s -prefix %(outfile)s -%(anat_type)s -time:zt %(slices)s %(bold_reps)s %(repetition_time)s seqplus %(input_dir)s/%(dcmglob)s" % locals()
                    run(cmd)
                # Remove Discarded Acquisitions Before Scanner reaches
                # Steady State
                run("3dcalc -a %(output_dir)s/%(outfile)s+orig.[%(skip)s..$] -expr 'a' -prefix %(output_dir)s/%(outfile)s.%(format)s" % locals)

                # Cleanup Initial Reconstruction BRIKs & HEADs (remove or zip).
                #rm $output_dir/${outfile}+orig.BRIK $output_dir/${outfile}+orig.HEAD
                run("gzip %(output_dir)s/%(outfile)s+orig.[BH]*" % locals())
            else:
                print "No Dicom files found. Probably from the Waisman Center."
        else:
            print "No anatomical processing required."
    print "++++ End Processing %s ++++" % (modality, )
                               
if __name__ == "__main__":
    parser = OptionParser(usage = """Determines modality of a directory of dicoms and reconstructs it into a .nii file accordingly.

    eg. 'dicom_recon.py -i ~/data7/pib/pilot/data_mri/raw/3502.../001 -o ~/data7/pib/pilot/data_mri/orig -p 3502' """)
    parser.add_option("-i", "--input_dir", help="Input directory")
    parser.add_option("-o", "--output_dir", help="Output directory")
    parser.add_option("-p", "--prefix", help="Output prefix")
    parser.add_option("-r", "--recon_type", help="Reconstruction type")
    
    (options, args) = parser.parse_args()
    do_recon(options.input_dir, options.output_dir, options.prefix, options.recon_type)

