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
```HUClin/
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

## 🔹 Installation

Clone this repository and install dependencies:

```bash
git clone https://github.com/yourusername/HUClin.git
cd HUClin
pip install -r requirements.txt





Main Python dependencies

pandas

numpy

scikit-learn

shap

openpyxl

🔹 Usage
1. Convert raw datasets

Each dataset has a preprocessing script. Example for CKD:

python preprocessing/CKD.py


This produces an encoded dataset (e.g., CKDNo.txt).
Then assign utilities:

python conversion/ckdconversion.py


This creates utility-formatted files for HUIM/HUSPM.

2. Run pattern mining (SPMF GUI)

We used the SPMF GUI
:

Open SPMF:

java -jar spmf.jar


Select algorithm: EFIM, USPAN, HGB, HUSRM, or FCHM

Input file: e.g., CKDYesHUIM.txt

Output file: e.g., CKD_patterns.txt

Set thresholds (minutil/minsup) as reported in the paper

Click Run algorithm and save results

(Optional: For automation, SPMF also supports CLI:)

java -jar spmf.jar run EFIM input.txt output.txt 50%

3. Preprocess mined patterns

Clean patterns and normalize lengths:

python pattern_postprocessing/preporcesspatterns2.py


This outputs cleaned files, ready for Weka.

4. Convert to ARFF and run classifiers (Weka GUI)

We used the Weka GUI
:

Open Weka GUI Chooser → Explorer

Load ARFF file (e.g., CKD_patterns.arff)

Choose classifier:

RandomForest

DecisionTree

Naive Bayes

kNN

SVM

Logistic Regression

MLP

Voting Ensemble

Select evaluation: 5-fold CV, 10-fold CV, or 80:20 split

Click Start

🔹 Datasets

The datasets used are publicly available:

Chronic Kidney Disease: Figshare

Disease Symptoms and Patient Profile: Kaggle

COVID-19 Surveillance: CDC

Heart Failure Prediction: Kaggle

Diabetes Dataset: Kaggle

FLChain Dataset: Figshare

⚠️ Note: Due to licensing and privacy, the raw datasets are not included in this repository.
Please download them from the above links.

🔹 Citation

If you use this code, please cite:

@article{YourName2025,
  title={HUClin: A High-Utility Framework for Mining Predictive Patterns in Electronic Health Records},
  author={Your Name and Co-authors},
  journal={Information Processing & Management},
  year={2025}
}
