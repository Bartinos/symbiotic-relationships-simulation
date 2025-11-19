# symbiotic-relationships-simulation

This project is an Agent Based Modeling solution for the course Multi Agent Systems at Tilburg University. The model aims to explore how symbiotic relationships, such as the mutualistic/commensal spider-frog relationship, are formed.

## Preparation to run the model

It is suggested to use a virtual environment such as [conda](https://www.anaconda.com/docs/getting-started/miniconda/install#windows-installation).

To see if it is installed, open a terminal and run: 

```bash 
conda --version
```

If the resulting output gives an error, please install conda [here](https://www.anaconda.com/docs/getting-started/miniconda/install#windows-installation).

### Step 1: clone the repo

First, `git clone` the repository. If you're not comfortable using git, it is recommended to use a simple git GUI such [GitKraken](https://www.gitkraken.com/).

### Step 2: set up the environment
Open a terminal in the repository directory and run the following:

```bash
conda create -n symbiotic python=3.11

conda activate symbiotic

pip install -r requirements.txt
```

### To use in vscode

Make sure the `Jupyter` extension is installed. You can check by going to `extensions` on the left of vscode and search for `Jupyter`.

If this is installed, open the notebook and in the top right corner, press `select kernel` and select the `symbiotic` environment. 
