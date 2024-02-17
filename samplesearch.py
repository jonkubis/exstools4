import os

def resolve_sample_locations(instrument):
    previously_found_paths = []
    exsfile_path = os.path.split(instrument.pathname)[0]
    user_path = os.path.expanduser("~")
    music_apps_path = os.path.join(user_path, "Music/Audio Music Apps/Sampler Instruments/")

    for s in instrument.samples:
        if s.filename is None: s.filename = s.name

        pathname = os.path.join(s.folder,s.filename)

        if os.path.exists(pathname): continue #pathname is correct and exists - move on!

        # okay -- the pathname doesn't exist.

        # first off, is it in the SAME folder as the EXS file?
        if os.path.exists(os.path.join(exsfile_path,s.filename)):
            s.folder = exsfile_path
            continue

        # is it in a folder with the same name as the instrument (as stored in the instrument file)?
        pathname_to_try = os.path.join(exsfile_path,instrument.name,s.filename)
        if os.path.exists(pathname_to_try):
            s.folder = os.path.split(pathname_to_try)[0]
            continue

        # is it in a folder with the same name as the EXS file?
        pathname_to_try = os.path.join(os.path.splitext(instrument.pathname)[0], s.filename)
        if os.path.exists(pathname_to_try):
            s.folder = os.path.split(pathname_to_try)[0]
            continue

        # let's see if this file was originally in the old Library/Application Support folder but has moved to the new Audio Music Apps folder
        if pathname.startswith('/Library/Application Support/Logic/Sampler Instruments/'):
            pathname_to_try = os.path.join(music_apps_path,pathname[55:])
            if os.path.exists(pathname_to_try):
                s.folder = os.path.split(pathname_to_try)[0]
                continue

        elif '/Library/Application Support/Logic/Sampler Instruments/' in pathname:
            pathname_to_try = pathname.replace('/Library/Application Support/Logic/Sampler Instruments/','/Music/Audio Music Apps/Sampler Instruments/')
            if os.path.exists(pathname_to_try):
                s.folder = os.path.split(pathname_to_try)[0]
                continue



        print ("CAN'T FIND ",pathname)

    all_samples_found = True
    for s in instrument.samples:
        if not os.path.exists(os.path.join(s.folder,s.filename)):
            all_samples_found = False
            break

    if all_samples_found: print ("All samples found!")


        #print (s.folder)
        #print (s.filename)
    quit()