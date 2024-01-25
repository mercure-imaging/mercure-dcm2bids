"""
m_dcm2bids.py
=============
Simple module to run dcm2bids conversion in mercure
"""

# Standard Python includes
import os
import sys
import stat
import json
import pydicom
import dcm2bids
import subprocess
import shutil
from pathlib import Path


def main(args=sys.argv[1:]):
    """
    DICOM to BIDS conversion module using the dcm2bids converter.
    """
    
    print(f"Starting mercure-dcm2bids converter.")

    # Check if the input and output folders are provided as arguments
    if len(sys.argv) < 3:
        print("Error: Missing arguments!")
        print("Usage: testmodule [input-folder] [output-folder]")
        sys.exit(1)

    # Check if the input and output folders actually exist
    in_folder = sys.argv[1]
    out_folder = sys.argv[2]
    if not Path(in_folder).exists() or not Path(out_folder).exists():
        print("IN/OUT paths do not exist")
        sys.exit(1)

    # Create default values for all module settings
    settings = {"source_data": "False", 
                "descriptions": [ #default searches only for a t1w mprage
                    {
                        "datatype": "anat",
                        "suffix": "T1w",
                        "criteria": {
                            "SeriesDescription": "*mprage*"
                        }
                    }
                    
                ]
                
                }

    
    # Set BIDS participant
    bidsID="ID0000001"
    scan_date=""
    scan_time=""
    for entry in os.scandir(in_folder):
        if entry.name.endswith(".dcm") and not entry.is_dir():
            # Load slice
            dcm_file = Path(in_folder) / entry.name
            ds = pydicom.dcmread(dcm_file)
            PI = ds.PatientID
            ACC = ds.AccessionNumber
            if (ds.StudyDate !="") and (scan_date== ""):
                scan_date=ds.StudyDate
            if (ds.StudyTime !="") and (scan_time== ""):
                scan_time=ds.StudyTime
            
            if ACC != "":
                bidsID = ACC
                break
    
    print(f"Converting patient ID : ", bidsID )
    
    # Generate dcm2bids scaffold folder structure to create valid BIDS output
    results_dir = 'BIDS_' + bidsID + '_' + PI + '_DATE_' + scan_date +'_TIME_' + scan_time.split('.')[0]
    current_dir = os.getcwd()
    results_path = os.path.join(current_dir, results_dir)
    if not os.path.exists(results_path):
        os.umask(0)
        os.makedirs(results_path)
    p = Path(results_path)
    p.chmod(p.stat().st_mode | stat.S_IROTH | stat.S_IXOTH | stat.S_IWOTH)
    
    # create BIDS directory structure
    subprocess.run(["dcm2bids_scaffold","-o", results_path, "--force"])
    
    # Load the task.json file, which contains the settings for the processing module
    try:
        with open(Path(in_folder) / "task.json", "r") as json_file:
            task = json.load(json_file)
    except Exception:
        print("Error: Task file task.json not found")
        sys.exit(1)
    
    
     # Overwrite default values with settings from the task file (if present)
    if task.get("process", ""):
        settings.update(task["process"].get("settings", {}))
    
    # Get dcm2bids config and write configuration file
    bids_config = {"descriptions":settings["descriptions"]}
    config_path = os.path.join(results_path, 'derivatives')
    if Path(config_path).exists():
        config_file = os.path.join(config_path,"dcm2bids_config.json")
    with open(config_file, "w") as write_file:
        json.dump(bids_config, write_file, indent=4)
    p = Path(config_file)
    p.chmod(p.stat().st_mode | stat.S_IROTH | stat.S_IXOTH | stat.S_IWOTH)

    # output directory info
    print(f"The input folder is: ", in_folder)
    print(f"The output folder is: ", out_folder)
    print(f"The json file is: ", config_file)

   
    # Copy source data to output if selected (default befaviour is False).
    source_path = in_folder
    source_copy=settings["source_data"]
    if(source_copy=='True'):
        source_path = os.path.join(results_path, 'sourcedata')
        if Path(source_path).exists():
            for file in os.listdir(in_folder):
                if file.endswith(".dcm"):
                    if '#' in file:
                        # Split the filename using the string '#'
                        dest_file = file.split('#')[-1]
                    else:
                        dest_file = file
                    shutil.copy(os.path.join(in_folder, file), os.path.join(source_path,dest_file))

    # Run dcm2bids conversion
    subprocess.run(["dcm2bids", "-d", source_path, "-p",bidsID, "-c", config_file,"-o", results_path,"--auto_extract_entities"])

    for root, dirs, files in os.walk(results_path):
        for d in dirs:
            os.chmod(os.path.join(root, d), 0o777)
        for f in files:
            os.chmod(os.path.join(root, f), 0o777)

    # Remove temporary dcm2nixx conversions
    temp_bids_dir = os.path.join(results_path, "tmp_dcm2bids")
    if os.path.isdir(temp_bids_dir):
        shutil.rmtree(temp_bids_dir)
    
    # zip BIDS directory structure and send to output directory
    shutil.make_archive(results_dir, format='zip', root_dir=current_dir, base_dir=results_dir)
    out_file = os.path.join(current_dir, results_dir + '.zip')
    if Path(out_file).exists():
        shutil.move(out_file, out_folder)

    # mercure requires .dcm file to trigger routing, generate a dummy .dcm file to route BIDS results
    dcm_file_name = os.path.join(current_dir, 'routing_trigger.dcm')
    with open(dcm_file_name, 'w') as f:
        f.write('Routing trigger file.')
    
    if Path(dcm_file_name).exists():
        shutil.move(dcm_file_name, out_folder)


if __name__ == "__main__":
    main()
