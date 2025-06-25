@echo off
echo Installing dependencies for pop2piano...

echo Creating virtual environment...
py -3 -m venv venv

echo Installing numpy < 2...
venv\Scripts\python.exe -m pip install "numpy<2"

echo Installing basic dependencies...
venv\Scripts\python.exe -m pip install librosa soundfile
venv\Scripts\python.exe -m pip install torch==1.13.1 torchaudio==0.13.1

echo Installing essentia...
venv\Scripts\python.exe -m pip install essentia==2.1b5

echo Installing remaining dependencies...
venv\Scripts\python.exe -m pip install pretty-midi==0.2.9
venv\Scripts\python.exe -m pip install omegaconf==2.1.1
venv\Scripts\python.exe -m pip install transformers==4.16.1
venv\Scripts\python.exe -m pip install pytorch-lightning==1.8.4
venv\Scripts\python.exe -m pip install note-seq==0.0.5
venv\Scripts\python.exe -m pip install pyFluidSynth==1.3.0
venv\Scripts\python.exe -m pip install yt-dlp

echo Testing imports...
venv\Scripts\python.exe test_imports.py

echo Done!
pause 