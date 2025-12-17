# Easy_Chatterbox
Easy one shot installer for configuring Chatterbox's TTS models (Original and Turbo)

# Why?

Chatterbox on it's own is not fun to setup, especially since it has in the past fucked with my python install. Very fun isn't it? You need very specific dependencies and files for this to run, so I said "Fuck it, let's just make a script to install this goddamn model". Resulting in this.

# Example

![img](https://i.postimg.cc/Mp3MCJMb/image.png)

# What Does This Work On?

Can tell you it works well under linux, Debian specifically. Given the specific requirements, this is also meant mostly for Python 3.11.9, Python 3.13 right now seems impossible to use to get Chatterbox running. Windows *should* work when using powershell, however, under CMD, it is known to just straight up not work. Typical CMD 🙄.

Most modern linux systems come with a newer version of python than 3.11.9, so make sure you also use pyenv to install 3.11.9, you can find that [here](https://github.com/pyenv/pyenv).

# Usage

`python ChatterboxInstaller.py`
`python GUI_v2.py`

# Requirements

- Python 3.11.9
- Linux or Windows (Windows support may be incomplete at this time, Linux is your best bet)
- ROCm: Linux Only, Radeon RX 6000 and newer
- CUDA: Linux and Windows: RTX 30 and newer, RTX 20 MAY work, no support in the script though
- CPU: Any, note that this is the slowest method of generating audio

Disk Space:

Turbo (350m): 4.06GB
Original (500m): 9.06GB

# Project Pages

Chatterbox (Original): https://huggingface.co/ResembleAI/chatterbox/tree/main
Chatterbox (Turbo): https://huggingface.co/ResembleAI/chatterbox-turbo
Flash Attention Wheels: https://github.com/mjun0812/flash-attention-prebuild-wheels

# Disclaimer

Code was made by Claude Sonnet 4.5, it is not perfect and it is not expected to be. This is just meant as an easier way to install and run the model. Do not use this code in production please :)
