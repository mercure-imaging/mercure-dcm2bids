"""
m_dcm2bids.py
=============
Simple module to run dcm2bids conversion in mercure
"""

# Standard Python includes
import os
import sys
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
    settings = {"source_data": "True", 
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

    current_dir = os.getcwd()
    config_file = os.path.join(current_dir,"dcm2bids_config.json")
    with open(config_file, "w") as write_file:
        json.dump(bids_config, write_file, indent=4)
    
    # check if the task.json file exists
    print(f"The input folder is: ", in_folder)
    print(f"The output folder is: ", out_folder)
    print(f"The json file is: ", config_file)

    # Set BIDS participant
    bidsID="ID0000001"
    for entry in os.scandir(in_folder):
        if entry.name.endswith(".dcm") and not entry.is_dir():
            # Load slice
            dcm_file = Path(in_folder) / entry.name
            ds = pydicom.dcmread(dcm_file)
            PI = ds.PatientID
            ACC = ds.AccessionNumber
            if PI != "":
                bidsID = PI
                accID = ACC
                break
    
    print(f"Converting patient ID : ", bidsID )
    
    # Generate dcm2bids scaffold folder structure to create valid BIDS output
    results_path = os.path.join(current_dir, 'BIDS_' + bidsID + "_" + accID)
    if not os.path.exists(results_path):
        os.makedirs(results_path)
    
    subprocess.run(["dcm2bids_scaffold","-o",results_path])

    # Copy source data to output if selected (default befaviour is True).
    source_path = in_folder
    source_copy=settings["source_data"]
    if(source_copy=='True'):
        source_path = os.path.join(results_path, 'sourcedata')
        if Path(source_path).exists():
            for file in os.listdir(in_folder):
                if file.endswith(".dcm"):
                    shutil.move(os.path.join(in_folder, file), source_path)

    # Run dcm2bids conversion
    subprocess.run(["dcm2bids", "-d", source_path, "-p",bidsID, "-c", config_file,"-o", results_path,"--auto_extract_entities"])

    # Remove temporary dcm2nixx conversions
    temp_bids_dir = os.path.join(results_path, "tmp_dcm2bids")
    if os.path.isdir(temp_bids_dir):
        shutil.rmtree(temp_bids_dir)

    # Copy results to output
    if Path(results_path).exists():
        shutil.move(results_path, out_folder)


if __name__ == "__main__":
    main()
