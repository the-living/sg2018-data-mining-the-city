import json
import os
import argparse
import reconstruct
import time
import datetime

def elapsedTime(start, end):
    return str(datetime.timedelta(seconds=end-start))

def run():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", help="Enable Verbose Output",
        action="store_true")
    ap.add_argument("-i", "--input", help="Input JSON")
    args = vars(ap.parse_args())

    VERBOSE = args["verbose"]

    assert os.path.exists(args["input"]), "ERROR: Input JSON missing at {}".format(args["input"])
    f = open(args["input"], mode='r')
    scheduler = json.load(f)
    f.close()

    for build in scheduler:
        if build["COMPLETE"]:
            if VERBOSE: print "{} already completed".format(build["NAME"])
            continue

        if VERBOSE: print("Building {}\n".format(build["NAME"]))
        start_time = time.time()
        reconstruct.build_reconstruction(build)

        duration = elapsedTime(start_time, time.time())
        if VERBOSE: "{} Complete! / {}".format(build["NAME"],duration)
        build["COMPLETE"] = True
        build["COMPLETE_TIME"] = duration

        json.dump(
            scheduler,
            open(args["input"],mode='w'),
            sort_keys=True,
            indent=4,
            separators=(',', ': '))

if __name__ == "__main__":
    run()
