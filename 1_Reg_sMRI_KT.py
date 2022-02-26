#!/tools/Python/Python-3.8.0/bin/python3
## adapted by M Styner, original script by SunHyung 
## changed to python3
## removed bias corrected by Karlie Tong
## added support for brainmask => significantly improved results
## added support for optional initial T1 transform file 
##           => allows update with initial transform in case of failures
## replaced linear interpolation by b-spline interpolation
## added removal of negative scalars from final image
######################################################################################################### 

import os
import sys
import glob
import subprocess
from optparse import OptionParser

Current_Dir = os.getcwd()

DATADIR = "/ASD/Autism/IBS/Proc_Data/"
PREFIX = ""

# infant nih pd atlas as template
ATLAS = '/NIRAL/tools/atlas/MNI_ATLASES/IBIS/1year-Average-IBIS-MNI-t1W.nrrd'
MASK = '/NIRAL/tools/atlas/MNI_ATLASES/IBIS/1year-Average-IBIS-MNI-mask.nrrd'
PROCDIR = "Proc_T1T2_v1.0"

#tools
BRAINSFITCmd = '/tools/bin_linux64/BRAINSFit'
ResampleCmd = '/tools/bin_linux64/ResampleScalarVectorDWIVolume'
#N4Cmd = '/tools/bin_linux64/N4BiasFieldCorrection'
ImageMathCmd = '/tools/bin_linux64/ImageMath'

def main(opts, argv):

        CASE_LIST = []	
        if (argv[0] == "all"):
                CASE_LIST = sorted(glob.glob(DATADIR + "/" + PREFIX + "*[0123456789][0123456789B]"+ "/V[012][624]"))

        else:
                CASE_LIST = [ DATADIR + "/" + PREFIX + argv[0] ]

        #print(CASE_LIST)

        if (os.path.exists(MASK)):
                use_mask = True

        for CASE_FOLDER in CASE_LIST :
                SMRI_FOLDER = CASE_FOLDER + "/mri/native/sMRI"
                T1 = ""
                T2 = ""
                ID = os.path.basename(CASE_FOLDER)

                #select the images to register
                if (os.path.exists(SMRI_FOLDER)):
                        T1_FILELIST = glob.glob(SMRI_FOLDER + "/*_t1*.nrrd")
                        T2_FILELIST = glob.glob(SMRI_FOLDER + "/*_t2*.nrrd")

                        if (len(T1_FILELIST) < 1):
                                print ("WARNING: no T1's in " + SMRI_FOLDER)
                        elif (len(T1_FILELIST) > 1): 
                                # check if there is a selected case
                                SELLIST = glob.glob(SMRI_FOLDER + "/*_T1*select.nrrd")
                                if (len(SELLIST) < 1):
                                        print ("WARNING: more than one T1 in " + SMRI_FOLDER + " , but no file selected : # " + str(len(T1_FILELIST)))
                                        command = "echo " + str(len(T1_FILELIST)) + " > " +  SMRI_FOLDER + "/NumT1.txt"
                                        #print(command)
                                        subprocess.run(command, shell=True)
                                else:
                                        T1 = SELLIST[0]
                                        if (not os.path.exists(T1)):
                                                print("T1 bad link? " + T1)
                        else:
                                T1 = T1_FILELIST[0]

                        if (len(T2_FILELIST) < 1):
                                print ("WARNING: no T2's in " + SMRI_FOLDER)
                        elif (len(T2_FILELIST) > 1):
                                # check if there is a selected case
                                SELLIST = glob.glob(SMRI_FOLDER + "/*_T2*select.nrrd")
                                if (len(SELLIST) < 1):
                                        print ("WARNING: more than one T2 in " + SMRI_FOLDER + " , but no file selected for processing")
                                        command = "echo " + str(len(T2_FILELIST)) + " > " +  SMRI_FOLDER + "/NumT2.txt"
                                        subprocess.run(command, shell=True)
                                else:
                                        T2 = SELLIST[0]
                                        if (not os.path.exists(T2)):
                                                print("T2 bad link? " + T2)
                        else:
                                T2 = T2_FILELIST[0]

                        #print(T1 + " " + T2)
	
                #register the images to the template
                if (os.path.exists(T1) or os.path.exists(T2)):

                        #print ("Doing " + ID)
                        PROC_FOLDER = SMRI_FOLDER + PROCDIR
                        if (not os.path.exists(PROC_FOLDER)):
                                os.mkdir(PROC_FOLDER)

	
                        STX_T1 = PROC_FOLDER + '/stx_' + ID + "_T1_bs.nrrd"
                        STX_T2 = PROC_FOLDER + '/stx_' + ID + "_T2_bs.nrrd"
                        STX_T1_transform = PROC_FOLDER + '/stx_rigid_transformT1.txt'
                        STX_T2_transform = PROC_FOLDER + '/stx_rigid_transformT2.txt'
                        STX_T1_transform_init = PROC_FOLDER + '/stx_rigid_transformT1_init.txt'
                        STX_T2_transform_init = PROC_FOLDER + '/stx_rigid_transformT2_init.txt'

                        # register the T1 images
                        if (not os.path.exists(STX_T1)):
                                print ("running atlas registration T1 " + STX_T1) 
                                
                                if (use_mask):
                                        print ("using mask " )
                                        #print (["%s --fixedVolume %s --movingVolume %s --useAffine --initializeTransformMode useCenterOfHeadAlign --numberOfSamples 600000 --linearTransform %s" %(BRAINSFITCmd, ATLAS, T1, STX_T1_transform) ])
                                        # start with affine to get brain mask to individual space
                                        if (os.path.exists(STX_T1_transform_init)):
                                                subprocess.run(["%s --fixedVolume %s --movingVolume %s --useAffine --numberOfSamples 600000 --initialTransform %s --linearTransform %s" %(BRAINSFITCmd, ATLAS, T1, STX_T1_transform_init, STX_T1_transform) ], 
                                                               shell=True) 
                                        else:
                                                #print(["%s --fixedVolume %s --movingVolume %s --useAffine --initializeTransformMode useCenterOfHeadAlign --numberOfSamples 600000 --linearTransform %s" %(BRAINSFITCmd, ATLAS, T1, STX_T1_transform) ])
                                                subprocess.run(["%s --fixedVolume %s --movingVolume %s --useAffine --initializeTransformMode useCenterOfHeadAlign --numberOfSamples 600000 --linearTransform %s" %(BRAINSFITCmd, ATLAS, T1, STX_T1_transform) ], 
                                                               shell=True) 
                                                
                                        MASK_INDIV = PROC_FOLDER + '/brainmaskAtlasToIndiv_Tmp.nrrd'
                                        # applies the inverse to get brainmask into indiv space
                                        subprocess.run(["%s %s %s -f %s -R %s -i nn -b" %(ResampleCmd, MASK, MASK_INDIV, STX_T1_transform, T1)], 
                                                       shell=True)
                                        
                                        print ("updating atlas registration T1 (with mask) " + STX_T1) 
                                                
                                        if (os.path.exists(STX_T1_transform_init)):
                                                subprocess.run(["%s --fixedVolume %s --movingVolume %s --useRigid  --numberOfSamples 600000 --fixedBinaryVolume %s --movingBinaryVolume %s --initialTransform %s --linearTransform %s --maskProcessingMode ROI" %(BRAINSFITCmd, ATLAS, T1, MASK, MASK_INDIV, STX_T1_transform_init, STX_T1_transform) ], 
                                                               shell=True)
                                        else:
                                                subprocess.run(["%s --fixedVolume %s --movingVolume %s --useRigid --initializeTransformMode useCenterOfHeadAlign --numberOfSamples 600000 --fixedBinaryVolume %s --movingBinaryVolume %s --linearTransform %s --maskProcessingMode ROI" %(BRAINSFITCmd, ATLAS, T1, MASK, MASK_INDIV, STX_T1_transform) ], 
                                                               shell=True)

                                        # remove mask, as it was only temporarily used
                                        os.remove(MASK_INDIV)

                                else:
                                        subprocess.run(["%s --fixedVolume %s --movingVolume %s --useRigid --initializeTransformMode useCenterOfHeadAlign --numberOfSamples 600000 --linearTransform %s" %(BRAINSFITCmd, ATLAS, T1, STX_T1_transform) ], 
                                                       shell=True) 
                                        

                                #resample output image
                                subprocess.run(["%s %s %s -f %s -R %s -i bs -t rt" %(ResampleCmd, T1, STX_T1, STX_T1_transform, ATLAS)], 
                                               shell=True)
                                subprocess.run(["%s %s -outfile %s -threshMask 0,100000" %(ImageMathCmd,STX_T1,STX_T1)], shell=True)

                        #register the T2 images to the already registered T1    
                        if (not os.path.exists(STX_T2) and os.path.exists(STX_T1) and os.path.exists(T2)):
                                print ("running atlas T1 registration T2 " + STX_T2)
                                subprocess.run(["%s --fixedVolume %s --movingVolume %s --useRigid  --numberOfSamples 600000 --initialTransform %s --linearTransform %s" %(BRAINSFITCmd, STX_T1, T2, STX_T1_transform, STX_T2_transform)], 
                                               shell=True) 
                                subprocess.run(["%s %s %s -f %s -R %s -i bs -t rt" %(ResampleCmd, T2, STX_T2, STX_T2_transform, ATLAS)], 
                                               shell=True)
                                subprocess.run(["%s %s -outfile %s -threshMask 0,100000" %(ImageMathCmd, STX_T2, STX_T2)], shell=True)


                #end of if

#end of main 

	
if (__name__ == "__main__"):
        parser = OptionParser(usage="%prog [options] ID \n if ID = 'all' then do all cases, otherwise provide ID of case (without prefix " + PREFIX + ")")
        #parser.add_option("-o","--changeOrient",action="store_true", dest="orientation", default="False", help="if input data orientation is LPI, change the orientation RAI ")
        (opts, argv) = parser.parse_args()
        if (len(argv)<1):
                parser.print_help()
                sys.exit(0)
        main(opts, argv)


