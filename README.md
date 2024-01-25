# **mercure-dcm2bids**
<br>

Mercure module to perform DICOM to BIDS conversion using the [dcm2bids](https://github.com/UNFmontreal/Dcm2Bids) converter. dcm2bids reorganises NIfTI files using dcm2niix into the Brain Imaging Data Structure (BIDS). This module runs as a docker container in mercure, it can be added to an existing mercure installation using docker tag : *mercureimaging/mercure-dcm2bids*. The BIDS configuration .json content can be entered directly into the settings tab in the *Rules* or *Modules* pages of mercure's web-based interactive user interface. The module will generate a .zip file of the BIDS directory structure created using the dcm2bids scaffolding, including the original DICOM files in the *sourcedata* directory and converted BIDS data (see [dcm2bids documentation](https://unfmontreal.github.io/Dcm2Bids) for further details on the scaffold directory structure).

<br>

## **Installation**

### Add module to existing mercure installation
Follow instructions on [mercure website](https://mercure-imaging.org) on how to add a new module. Use the docker tag *mercureimaging/mercure-dcm2bids*.

<br>

### Build module for local testing, modification and development
1. Clone repo.
2. Build Docker container locally by running make (modify makefile with new docker tag as needed).
3. Test container :\
`docker run -it -v /input_data:/input -v /output_data:/output --env MERCURE_IN_DIR=/input  --env MERCURE_OUT_DIR=/output mercureimaging/mercure-dcm2bids`

<br>

### Quick start tutorial
Follow the ['First steps' tutorial](https://github.com/mercure-imaging/mercure-dcm2bids/blob/main/mercure_dcm2bids_first_steps_tutorial.ipynb) and setup an end-to-end mercure test environment for BIDS conversion on your local machine. The tutorial provides simple steps to guide installation of mercure with the mercure-dcm2bids module, and then to perform a BIDS conversion using a test DICOM dataset. It takes about one hour to complete.

<br>


## **Configuration**

### Define output directory in *Targets* page in mercure
The mercure-dcm2bids module requires an output directory for the zipped converted data. See example in image below for '/vagrant' directory. Click *test* button to ensure mercure can write to specified directory

<br>
<br>

![image](target.png)

<br>
<br>

### Add BIDS configuration file content 
The BIDS configuration for a project can be added to the 'Settings' tab in either the *Modules* or *Rules* pages. Adding the .json content to *Rules* is preferred to allow multiple BIDS configurations to coexist and run with a single dcm2bids module. More information on mercure rule configuration can be found [here](https://mercure-imaging.org/docs/usage.html#defining-rules). An example BIDS configuration based on the dcm2bids [first steps tutorial](https://unfmontreal.github.io/Dcm2Bids/docs/tutorial/first-steps/) is shown in the screenshot below.

<br>
<br>

![image](config.png)

<br>
<br>

Full configuration .json text for the first steps example:

~~~
{
  "descriptions": [
    {
      "id": "id_task-rest",
      "datatype": "func",
      "suffix": "bold",
      "custom_entities": "task-rest",
      "criteria": {
        "SeriesDescription": "Axial EPI-FMRI (Interleaved I to S)*"
      },
      "sidecar_changes": {
        "TaskName": "rest"
      }
    },
    {
      "datatype": "fmap",
      "suffix": "epi",
      "criteria": {
        "SeriesDescription": "EPI PE=*"
      },
      "sidecar_changes": {
        "intendedFor": ["id_task-rest"]
      }
    }
  ]
}
~~~

<br>

## **dcm2bids project**

### Information
Documentation: https://unfmontreal.github.io/Dcm2Bids/latest/

Ideas/New features: https://github.com/UNFmontreal/Dcm2Bids/issues

Questions/Issues: https://neurostars.org/tag/dcm2bids
<br>
### Acknowledgments
~~~
Boré, A., Guay, S., Bedetti, C., Meisler, S., & GuenTher, N. (2023). Dcm2Bids (3.1.1). Zenodo. https://doi.org/10.5281/zenodo.8436509
~~~

