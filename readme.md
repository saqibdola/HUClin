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
bash git clone https://github.com/yourusername/HUClin.git
cd HUClin
pip install -r requirements.txt
```

## 🔹 Usage
### 1. Convert raw datasets
Each dataset has a preprocessing script. Example for CKD:

```
bash python preprocessing/CKD.py 
```
This produces an encoded dataset (e.g., `CKDNo.txt`).   Then assign utilities:

``
bash python conversion/ckdconversion.py 
```

### 2. Run pattern mining (SPMF GUI)

We used the [SPMF GUI](http://www.philippe-fournier-viger.com/spmf/):
```
bash java -jar spmf.jar
```

1. Select algorithm: **EFIM**, **USPAN**, **HGB**, **HUSRM**, or **FCHM**  
2. Input file: e.g., `CKDYesHUIM.txt`  
3. Output file: e.g., `CKD_patterns.txt`  
4. Set thresholds (minutil/minsup) as reported in the paper  
5. Click **Run algorithm** and save results  

*(Optional: For automation, SPMF also supports CLI:)*
``
bash java -jar spmf.jar run EFIM input.txt output.txt 50%
```
### 3. Preprocess mined patterns

Clean patterns and normalize lengths:

```
bash python pattern_postprocessing/preporcesspatterns2.py 
```

### 4. Convert to ARFF and run classifiers (Weka GUI)

We used the [Weka GUI](https://www.cs.waikato.ac.nz/ml/weka/):

1. Open **Weka GUI Chooser** → **Explorer**  
2. Load ARFF file (e.g., `CKD_patterns.arff`)  
3. Choose classifier:  
   - RandomForest  
   - DecisionTree  
   - Naive Bayes  
   - kNN  
   - SVM  
   - Logistic Regression  
   - MLP  
   - Voting Ensemble  
4. Select evaluation: **5-fold CV**, **10-fold CV**, or **80:20 split**  
5. Click **Start**


