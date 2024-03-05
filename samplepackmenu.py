# ███████╗ █████╗ ███╗   ███╗██████╗ ██╗     ███████╗██████╗  █████╗  ██████╗██╗  ██╗███╗   ███╗███████╗███╗   ██╗██╗   ██╗   ██████╗ ██╗   ██╗
# ██╔════╝██╔══██╗████╗ ████║██╔══██╗██║     ██╔════╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝████╗ ████║██╔════╝████╗  ██║██║   ██║   ██╔══██╗╚██╗ ██╔╝
# ███████╗███████║██╔████╔██║██████╔╝██║     █████╗  ██████╔╝███████║██║     █████╔╝ ██╔████╔██║█████╗  ██╔██╗ ██║██║   ██║   ██████╔╝ ╚████╔╝
# ╚════██║██╔══██║██║╚██╔╝██║██╔═══╝ ██║     ██╔══╝  ██╔═══╝ ██╔══██║██║     ██╔═██╗ ██║╚██╔╝██║██╔══╝  ██║╚██╗██║██║   ██║   ██╔═══╝   ╚██╔╝
# ███████║██║  ██║██║ ╚═╝ ██║██║     ███████╗███████╗██║     ██║  ██║╚██████╗██║  ██╗██║ ╚═╝ ██║███████╗██║ ╚████║╚██████╔╝██╗██║        ██║
# ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝     ╚══════╝╚══════╝╚═╝     ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝╚═╝        ╚═╝
"""



if not os.path.isdir(pathname): sys.exit("Specified folder not found: " + pathname)
programfolder = pathname
singledir = False

for samplefilename in os.listdir(pathname):
    if samplefilename.endswith(".wav") or samplefilename.endswith(".aif"):
        singledir = True
        break

samplefolders = []
if (singledir == True):
    samplefolders.append(pathname)
else:
    for directory in os.listdir(pathname):
        if os.path.isdir(os.path.join(pathname, directory)):
            samplefolders.append(os.path.join(pathname, directory))

for thissamplefolder in samplefolders:
    samplepaths = []
    for samplefilename in os.listdir(thissamplefolder):
        if samplefilename.endswith(".wav") or samplefilename.endswith(".aif"):
            samplepaths.append(os.path.join(thissamplefolder, samplefilename))

    samplepaths.sort()  # alphabetize!
    # if (len(samplepaths) <= 61): #all will fit in a single preset
    instrumentname = os.path.split(thissamplefolder)[1]

    exs = EXSInstrument()  # create a new instrument
    exs.name = instrumentname
    exs.loadsamples(samplepaths)
    exsbasename = os.path.splitext(instrumentname)[0]
    samplenameprefix = ''.join(e for e in exsbasename if e.isalnum())
    if len(samplenameprefix) > 12:
        samplenameprefix = samplenameprefix[0:11] + samplenameprefix[-1:]
    exs.mergesamples(outfolderroot, samplenameprefix, None, False)
    exs.writeEXSfile(os.path.join(outfolderroot, exs.name + ".exs"), True)
"""
import glob
import os
import sys

import exsparams
from exsclasses import EXSInstrument, EXSZone
from samplemerge import samplemerge
from samplesearch import get_sample_info


def packsamples(sample_pathnames):
    inst = EXSInstrument()
    print (sample_pathnames)
    inst.name = os.path.split(os.path.split(sample_pathnames[0])[0])[1]

    midinote = 36
    for ctr, pathname in enumerate(sample_pathnames):
        s = get_sample_info(pathname)

        inst.samples.append(s)

        z = EXSZone()
        z.name = s.name
        z.id, z.sampleindex = ctr, ctr
        z.rootnote, z.startnote, z.endnote = midinote, midinote, midinote
        z.sampleend, z.loopend = s.length, s.length

        inst.zones.append(z)

        midinote += 1

    inst.params = exsparams.default_params

    return inst



def packfolder(folder_pathname, prefix=None, outpath=None):
    if not os.path.isdir(folder_pathname): sys.exit("Specified folder not found: " + folder_pathname)

    singledir = False # we're going to see if this is a folder-of-folders, or a folder of audio files

    for samplefilename in os.listdir(folder_pathname):
        if samplefilename.endswith(".wav") or samplefilename.endswith(".aif"):
            singledir = True; break # we found audio files, so let's pack ONLY this folder's contents

    preset_info = {}

    if singledir:
        name = os.path.split(folder_pathname)[1]
        preset_info[name] = {'path':folder_pathname}
    else:
        for d in os.listdir(folder_pathname):
            if os.path.isdir(os.path.join(folder_pathname, d)):
                name = os.path.split(folder_pathname)[1]
                preset_info[d] = {'path': os.path.join(folder_pathname,d), 'name': d}

    for p in preset_info.values():
        samplepaths = []
        for samplefilename in os.listdir(p['path']):
            if samplefilename.endswith(".wav") or samplefilename.endswith(".WAV") or samplefilename.endswith(".aif"):
                samplepaths.append(os.path.join(p['path'], samplefilename))

        samplepaths.sort()  # alphabetize!

        p['sample_paths'] = samplepaths

        inst = packsamples(p['sample_paths'])

        #if prefix is not None: inst.name = prefix + " " + inst.name

        #outpathname = os.path.join(outpath,inst.name+".exs")
        samplemerge(inst, output_path=outpath, prefix=prefix, original_param_data=False, original_group_data=False)





if __name__ == '__main__':
    folder_path = "/Users/jonkubis/Music/temp/DRUMS_IN_YOUR_FACE"
    packfolder(folder_path,outpath="/Users/jonkubis/Desktop/EXSOUT2/DRUMS IN YOUR FACE",prefix="DiyF")
    quit()

    #paths = glob.glob(os.path.join(folder_path,"*.wav"))

    #packsamples(paths)
    print (paths)
    quit()