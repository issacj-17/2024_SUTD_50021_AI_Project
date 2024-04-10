'''
Outputs (found in respective ds directories)
1. sol_mask.txt - solution mask
2. tsp_log.txt  - log of stuff that happened during concorde execution, time taken is stored here
3. pairwise.sol - solution generated by concorde
4. pairwise.tsp - converted pairwise csv to a tsp file for execution by concorde

'''
import os
import numpy as np
import pandas as pd
import subprocess

# EDIT THESE VARIABLES
# format of instances folder is expected to be same as Issac stored it
# e.g. instances/{number_of_depots}/{number_of_nodes}/{ds_#_courier_#}/{files}
instances_directory = "/Users/zhengwei/Documents/codeL/concordeTSPFileGeneration/instances"
path_to_concorde_exec = "/Users/zhengwei/Documents/codeL/concordeTSPFileGeneration/concorde"


def makeTspFile(pathToCSV):
    df = pd.read_csv(pathToCSV)
    np_csv = df.to_numpy()
    n = df.shape[0]
    np_csv = np.delete(np_csv, np.s_[0], axis=1)
    np_csv = np.around(np_csv, decimals=0).astype(np.int32)

    for i in range(n):
        np_csv[i][i] = 9999

    tsp_file = f'''NAME: {str(pathToCSV.split('/')[-2])}
TYPE: TSP
COMMENT: nil
DIMENSION: {n}
EDGE_WEIGHT_TYPE: EXPLICIT
EDGE_WEIGHT_FORMAT: FULL_MATRIX
EDGE_WEIGHT_SECTION\n'''

    for row in np_csv:
        for col in row:
            tsp_file += str(col) + " "
        tsp_file += "\n"

    output_path ='/'.join(pathToCSV.split('/')[:-1]) + "/pairwise.tsp"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w+") as f:
        f.write(tsp_file)


def directoryOfCsvToTsp(pathToDirectory):
    directory = os.fsencode(pathToDirectory)

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.startswith("ds_"):
            for f in os.listdir(os.path.join(directory,file)):
                fname = os.fsdecode(f)
                if fname == "pairwise.csv":
                    csv_path = os.fsdecode(os.path.join(directory, file,f))
                    makeTspFile(csv_path)


def runConcordeOnTspFiles(pathToDirectory):
    directory = os.fsencode(pathToDirectory)

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.startswith("ds_"):
            for f in os.listdir(os.path.join(directory,file)):
                fname = os.fsdecode(f)
                if fname == "pairwise.tsp":
                    out_file_path = (os.path.abspath(os.path.join(directory,file))).decode("ascii") + "/tsp_log.txt"
                    os.makedirs(os.path.dirname(out_file_path), exist_ok=True)
                    with open(out_file_path, "w+") as out_file:
                        os.chdir(os.path.join(directory,file).decode("ascii"))
                        subprocess.run([path_to_concorde_exec, (os.path.join(directory,file)).decode("ascii") + "/pairwise.tsp"], stdout=out_file)


def solToMask(filePath):
    with open(filePath, "r") as f:
        fileContents = f.readlines()
    l = []
    for i, line in enumerate(fileContents):
        if i == 0:
            continue
        l += map(lambda x: int(x), line.split())
    n = len(l)
    np_mask = np.zeros((n,n), dtype=np.int16)
    for i in range(0, n-1):
        path_from = l[i]
        path_to = l[i+1]
        np_mask[path_from][path_to] = 1
    outPath = "/".join(filePath.split("/")[:-1]) + "/sol_mask.txt"
    np.savetxt(outPath, np_mask)


def dirLevelSolMasking(pathToDirectory):
    # pathToDirectory is the dir one level above ds_ files
    directory = os.fsencode(pathToDirectory)

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.startswith("ds_"):
            for f in os.listdir(os.path.join(directory,file)):
                fname = os.fsdecode(f)
                if fname == "pairwise.sol":
                    out_file_path = (os.path.abspath(os.path.join(directory,file))).decode("ascii") + "/tsp_log.txt"
                    solToMask(os.path.abspath(os.path.join(directory,file,f)).decode("ascii"))
                    

def main():
    directory_in_str = instances_directory
    directory = os.fsencode(directory_in_str)
    for file in os.listdir(directory):
        for f in os.listdir(os.path.join(directory, file)):
            directoryOfCsvToTsp(os.path.join(directory, file, f))
            runConcordeOnTspFiles(os.path.join(directory, file, f))
            dirLevelSolMasking(os.path.join(directory, file, f))


if __name__ == "__main__":
    main()
