
# 🎧 YouTube Audio & Caption Downloader




## ✨ Why This Project Was Built
This project was built to automate the process of downloading audio from YouTube and obtaining manual captions. By focusing on mixed-language captions (Arabic and English), it provides a convenient tool for researchers or developers working on multilingual data or audio-related applications.





## 🛠 Problem It Solves
Manually downloading audio and extracting captions from YouTube is time-consuming and often complex, especially for large channels or playlists. This project automates the process, allowing you to quickly:
- Fetch audio from YouTube 🎶
- Split it into chunks based on caption timings ✂️
- Save captions and metadata easily 📝




## 🚀 Features
- 📥 Download audio from individual YouTube **videos**, **channels**, or **playlists**.
- 🌐 Extract and filter captions, focusing on mixed **Arabic** and **English** content.
- ✂️ Cut the audio into segments based on caption timestamps.
- 📝 Automatically generate a **metadata** file containing audio file names and corresponding captions.




## 🖥 How to Run the Code



### 1. 📦 Prerequisites

Make sure you have the following Python libraries installed:

- Install dependencies from the `requirements.txt`:

```bash
pip install -r requirements.txt
```


### 2. 📄 Prepare the Input



- Create a text file (e.g., `youLinks.txt`) containing the YouTube URLs (one per line) that you want to process.

### 3. 🏃 Run the Script



Run the script using the following format:

```bash
python main.py --link_type [video|channel|playlist] --audio_type [ar_only|en_only|all_mix|mix_only] --output_dir [path_to_output] --urls_file [path_to_urls_file] --caption_type [a|m] --caption_lang [ar|en]
```


#### Arguments:
- `--link_type`: Specify the type of YouTube link (`video`, `channel`, or `playlist`).
- `--audio_type`: Select either `all_mix` audio or only those with `mix_only` (Arabic and English) captions `ar_only` for only arabic `en_only` for only english.
- `--output_dir`: Specify the output directory for audio files.
- `--urls_file`: Path to the text file containing YouTube URLs.
- `--caption_type`: either `a` for auto-gen captions and `m` for manual-gen captions.
- `--caption_lang`: `ar` for arabic `en` for english.


### 💡 Example Command

```bash
python main.py --link_type video --audio_type all_mix --output_dir output --urls_file youLinks.txt --caption_type m --caption_lang ar 
```

and these is the defult ones so if you type `python main.py` only it should work as well


### 4. 📂 Output


The script will generate:
- 🎶 Audio chunks saved in the specified output directory.
- 🗒️ A `metadata` folder, containing files each file contains the name of each audio chunk and its corresponding caption.



