PyTEAL Application Demo
------------------------

Experimental interface to allow a more logical organization for application Smart Contract definition.

Install the [sandbox](https://github.com/algorand/sandbox)

Start the sandbox in dev mode
```sh
./sandbox up dev
```

Get account to use
```
./sandbox goal account list
./sandbox goal account export -a $ADDR_FROM_LIST
```

Paste mnemonic into demo.py, ovewriting the existing one and change the host/port/token to whatever you've got locally (usually port 4001)

TODO: provide method to pull from sandbox

If you've got all the requirements from ../requirements.txt, Run
```
python demo.py
```

This will create the teal source from the KitchenSink application, create the application on chain, call several methods, then destroy the application.
