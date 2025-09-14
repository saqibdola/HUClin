# HUClin: High-Utility Framework for Mining Predictive Patterns in EHRs

This repository contains the code, scripts, and instructions to reproduce the experiments from the paper:

**HUClin: A High-Utility Framework for Mining Predictive Patterns in Electronic Health Records**

## 🔹 Overview

HUClin is a pipeline for:

- **Encoding** raw clinical datasets into an integer-based representation  
- **Assigning utilities** to features using SHAP  
- **Mining patterns** with the [SPMF](http://www.philippe-fournier-viger.com/spmf/) software  
- **Preprocessing patterns** for consistency and classifier input  
- **Running classification experiments** in [Weka](https://www.cs.waikato.ac.nz/ml/weka/)  

## 🔹 Repository Structure
```
HUClin/
├── preprocessing/             # Convert raw datasets into encoded integer format
│   ├── CKD.py
│   ├── Diabetes.py
│   ├── DSPP.py
│   ├── HeartFailure.py
│   ├── COVID.py
│   └── FLChain.py
│
├── conversion/                # Assign utilities & prepare datasets for HUIM/HUSPM
│   ├── ckdconversion.py
│   └── ...
│
├── pattern_postprocessing/    # Clean & normalize mined patterns
│   ├── preporcesspatterns.py
│   └── preporcesspatterns2.py
│
├── examples/                  # Sample input/output (toy data, not patient records)
│
├── docs/                      # Paper figures, diagrams
│
├── requirements.txt           # Python dependencies
├── LICENSE
└── README.md

```



## 🔹 Installation

Clone this repository and install dependencies:

```
bash git clone https://github.com/yourusername/HUClin.git cd HUClin pip install -r requirements.txt
```
