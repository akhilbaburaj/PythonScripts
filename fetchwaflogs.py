import os, sys, ndjson, re, json
folder = sys.argv[1]
outputfile = sys.argv[2]
# List out files from the directory mentioned
waf_files = os.listdir(folder)
# Iterate through all of the log files one by one
for subdir, dirs, waf_files in os.walk(folder):
    for waf_file in waf_files:
        with open(os.path.join(subdir,waf_file)) as log_file:
            logs = ndjson.load(log_file)
            print("Checking File...:"+waf_file)
# Pull each NDJSON one by one and check for matches of COUNT, BLOCK or EXCLUDED_AS_COUNT. If yes, write to new File.
            for log in logs:
                if re.search("'action': 'BLOCK'",str(log)) or re.search("'action': 'COUNT'",str(log)) or re.search("'exclusionType': 'EXCLUDED_AS_COUNT'",str(log)):
                    print("Hit a Request! Writing to file...")
                    fout = open(outputfile, "a+")
                    fout.write(json.dumps(log))
                    fout.close()
print("Pushed all matching logs to file : "+outputfile)
