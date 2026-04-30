# pipeline

## First-Time Set-Up Instructions

This guide will walk you through how to set up and generate nools and corresponding maps for the nmap tutor locally. The following commands should be run in your terminal.

1. Clone the repo:

```
git clone https://github.com/micosu/nmap-tutor
cd nmap/pipeline
```

2. Make a Virtual Environment

- On Mac

```
python3 -m venv venv OR python -m venv venv (try both, see which works)
source venv/bin/activate
```

- On Windows:

```
python -m venv venv
source venv\Scripts\activate
```

3. Install dependencies:

```
pip install -r requirements.txt
```

After that, you should be ready to generate problems!

## Generating New Problems

You can generate new problems running auto_generate.py like so:

```
python auto_generate.py --prob_type "Problem Type" --subnets 1 --q_type "pretest"
```

The following parameters are required:

- --prob_type: The problem type you would like to generate, wrapped in quotes. Currently, auto_generate.py only supports the following options: "Bad Ports", "Identify Services", "Rogue Workstations", "Unresponsive Workstations"
- --subnets: The number of subnets you would like the problem to have, not wrapped in quotes. The code works well with up to 4 subnets, though when calling it with 3 subnets the map may look a little misaligned

The following parameters are optional:

- --q_type: The type of question you would like to generate, wrapped in quotes. This can be either "pretest", "posttest" or "normal". The default value is "normal". The main difference between normal questions and test questions is the introtxt, and some problem types change the context so that it looks different than practice questions.
- --folder: The folder where you want the nools file to be stored, wrapped in quotes. Default folder name is "exampleFiles".
- --images_folder: The folder where you want the associated images to be stored, wrapped in quotes. Default image folder name is "images".

## Key Files

- network.py: The code used to generate the network maps. If you want to quickly generate just a single network map with one subnet, edit the "base_ip" and "prefix_length" variables and change the file name (if desired). Then you can run the file and a map will be generated and stored locally
- problem.py: The code that contains information on the different problem types ("Bad Ports", "Identify Services", etc)
- auto_generate.py: Relies on code from network.py and problem.py to implement a full pipeline, starting with information on the problem type and number of subnets provided to the arg parser when you run the files.
