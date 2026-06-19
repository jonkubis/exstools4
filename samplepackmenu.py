# ███████╗ █████╗ ███╗   ███╗██████╗ ██╗     ███████╗██████╗  █████╗  ██████╗██╗  ██╗███╗   ███╗███████╗███╗   ██╗██╗   ██╗   ██████╗ ██╗   ██╗
# ██╔════╝██╔══██╗████╗ ████║██╔══██╗██║     ██╔════╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝████╗ ████║██╔════╝████╗  ██║██║   ██║   ██╔══██╗╚██╗ ██╔╝
# ███████╗███████║██╔████╔██║██████╔╝██║     █████╗  ██████╔╝███████║██║     █████╔╝ ██╔████╔██║█████╗  ██╔██╗ ██║██║   ██║   ██████╔╝ ╚████╔╝
# ╚════██║██╔══██║██║╚██╔╝██║██╔═══╝ ██║     ██╔══╝  ██╔═══╝ ██╔══██║██║     ██╔═██╗ ██║╚██╔╝██║██╔══╝  ██║╚██╗██║██║   ██║   ██╔═══╝   ╚██╔╝
# ███████║██║  ██║██║ ╚═╝ ██║██║     ███████╗███████╗██║     ██║  ██║╚██████╗██║  ██╗██║ ╚═╝ ██║███████╗██║ ╚████║╚██████╔╝██╗██║        ██║
# ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝     ╚══════╝╚══════╝╚═╝     ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝╚═╝        ╚═╝
import os
import sys

import exsparams
from exsclasses import EXSInstrument, EXSZone
from consolidate import consolidate
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
        z.Name = s.Name
        z.id, z.FileName = ctr, ctr
        z.KeyNote, z.FirstNote, z.LastNote = midinote, midinote, midinote
        z.EndFrame, z.SustainLoopEnd = s.frameCount, s.frameCount

        inst.zones.append(z)

        midinote += 1

    inst.params = exsparams.default_params

    return inst



def packfolder(folder_pathname, prefix=None, outpath=None, codec="lpcm"):
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
        # get_sample_info already set absolute folder/filename, so skip re-resolution
        consolidate(inst, outpath, codec=codec, prefix=prefix, resolve=False,
                    original_param_data=False, original_group_data=False)





if __name__ == '__main__':
    folder_path = "/Users/jonkubis/Music/temp/DRUMS_IN_YOUR_FACE"
    packfolder(folder_path,outpath="/Users/jonkubis/Desktop/EXSOUT2/DRUMS IN YOUR FACE",prefix="DiyF")
    quit()

    #paths = glob.glob(os.path.join(folder_path,"*.wav"))

    #packsamples(paths)
    print (paths)
    quit()