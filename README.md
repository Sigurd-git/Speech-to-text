# Speech-to-text
Use azure speech service to do speech-to-text task
Hint: You can not run it on Bluehive.

## Usage
1. Create a new azure speech service resource

2. Install azure-cognitiveservices-speech package
```
conda env create -f environment.yml
conda activate STT
```

3. Run the code

```
AZURE_SPEECH_KEY=<your_key> AZURE_SPEECH_REGION=<your_region> python STT.py
```

