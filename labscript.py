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