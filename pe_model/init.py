# init.py
''' Read init.json and provides constants to other modules 
Creates output subdirectories if theuy do not already exist'''

from pathlib import Path
import json

PARPATH = Path(Path(__file__).parent) /"params"
initfile = Path(Path(__file__).parent) /"init.json"

try: 
        with open(initfile, 'r') as openfile:
        # Reading from json file
            json_dict = json.load(openfile)
            PARPATH = Path(Path(__file__).parent) / json_dict["PARPATH"]
            PARFILE = PARPATH / json_dict["PARFILE"]
            TEXTPATH = Path(Path(__file__).parent) / json_dict["TEXTPATH"]
            FIGPATH  = Path(Path(__file__).parent) / json_dict["FIGPATH"]

            print(f"****** Sucessfully read {initfile}")
            
          
except FileNotFoundError:
        print(f"*** OOPS: {initfile} not found.\nReverting to defaults.")
        PARFILE = PARPATH / "params_default.json"

print(f"****** Parameter file = {PARFILE}")

for p in [TEXTPATH, FIGPATH]:
        if not p.exists():
                p.mkdir()