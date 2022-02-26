#!/tools/Python/Python-3.8.0/bin/python3
## adapted by M Styner, original script by SunHyung 
## bias corrected by Karlie Tong
## added support for brainmask => significantly improved results
## added support for optional initial T1 transform file 
##           => allows update with initial transform in case of failures
## replaced linear interpolation by b-spline interpolation
## added removal of negative scalars from final image
######################################################################################################### 

DATADIR = "/work/karliet/IBIS/Proc_Data/"
PREFIX = ""

#select the images to register
if (os.path.exists(SMRI_FOLDER)):
    T1_FILELIST = glob.glob(SMRI_FOLDER + "/*_t1*.nrrd")
    T2_FILELIST = glob.glob(SMRI_FOLDER + "/*_t2*.nrrd")
    
    if (len(T1_FILELIST) < 1):
        print ("WARNING: no T1's in " + SMRI_FOLDER)
    else:
        T1 = T1_FILELIST[0]
    
    if (len(T2_FILELIST) < 1):
        print ("WARNING: no T2's in " + SMRI_FOLDER)
    else:
        T2 = T2_FILELIST[0]



STX_T1 = PROC_FOLDER + '/stx_' + ID + "_T1_bs.nrrd"
STX_T2 = PROC_FOLDER + '/stx_' + ID + "_T2_bs.nrrd"
STX_T1_transform = PROC_FOLDER + '/stx_rigid_transformT1.txt'
STX_T2_transform = PROC_FOLDER + '/stx_rigid_transformT2.txt'
STX_T1_transform_init = PROC_FOLDER + '/stx_rigid_transformT1_init.txt'
STX_T2_transform_init = PROC_FOLDER + '/stx_rigid_transformT2_init.txt'

                  
if (not os.path.exists(STX_T1)):
    print ("running atlas registration T1 " + STX_T1) 