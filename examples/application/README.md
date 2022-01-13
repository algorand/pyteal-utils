PyTEAL Application Demo
------------------------

Experimental interface to allow a more logical organization for application Smart Contract definition.

Install the [sandbox](https://github.com/algorand/sandbox)

Start the sandbox in dev mode
```sh
./sandbox up dev
```

initialize a virtual environment
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

When you've got all the requirements, Run
```
python demo.py
```

This will create the teal source from the KitchenSink application, create the application on chain, call several methods, then destroy the application.