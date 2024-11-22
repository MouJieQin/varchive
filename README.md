<p align="center">
<img src="spa/src/assets/logo.svg" alt="Varchive" height=60 />
</p>

## Install

### IINA for Varchive

> Varchive relys on an video player, **[iina-for-varchive](https://github.com/MouJieQin/iina-for-varchive)** forked from the project  [iina](https://github.com/iina/iina)

Download the corresponding version of [release](https://github.com/MouJieQin/iina-for-varchive/releases). 

> Install it but do not open it.  Ensure that iina-for-varchive opens after the varchive server is launched.

### Desktop App

<p align="center">
<img src="electron/electron/build/icon.svg" alt="app.icon" height=100 />
</p>


Download the dmg in [releases](https://github.com/MouJieQin/varchive/releases). It will still open the terminal to install some dependencies when you open the app for the first time. You will be asked to input your system password during the process. I cannot ensure that the install process will work even though I tested it in a new virtual machine.

![app](https://github.com/MouJieQin/assets/blob/main/varchive/assets/app.png)



### Install through shell script

Clone this [repository](https://github.com/MouJieQin/varchive.git) by running 

   ```shell
git clone https://github.com/MouJieQin/varchive.git
   ````

```shell
cd varchive
./install
```

> You will be asked to type your system password during the process.
>
> The `install` should be able to install varchive automatically, or you may have to refer to the following steps.

### Install step by step 

#### Varchive Server

1. Install root certificate by running 

> [!IMPORTANT]
>
> The `./genCA` will generate your own root certificate to provide https serve demanded by IINA and Varchive.
>
> You will be asked to type your system password during the process.

   ```shell
   cd varchive/server/pem
   ./genCA
   ```

2. Install command line tools used to generate images from video and download video from network resources by running 

   ```shell
   brew install ffmpeg yt-dlp
   ```

3. Launch server

   > The server is developed by python3.9, so python3.9+ shoulde work too.
   >
   > The default config is https://127.0.0.1:8999.

   ```shell
   cd varchive/server/src
   python3.9 -m pip install -r requirements.txt
   python3.9 varchive-server.py
   ```

#### Varchive client

   Launch varchive client

   > Open another terminal tab to launch client.
   >
   > The default config is http://localhost:5999/

Install npm first if you don't have 

   ```shell
   brew install npm
   ```

```shell
cd varchive/spa
npm install
npm run dev
```


## Features/Usage

### A simple start

Open a video using [iina-for-varchive](https://github.com/MouJieQin/iina-for-varchive), press `a` key first then press `o` key. A varchive page of this video will be opened on your browser. (Note: you have to use iina defautl key bindings config to do it, or you have to config your key bindings first. )

![directory-navigation](https://github.com/MouJieQin/assets/blob/main/varchive/assets/directory.mov.gif)

When you open a local video using [iina-for-varchive](https://github.com/MouJieQin/iina-for-varchive) and archive the video by the keyboard shortcut `a`(default key), a varchive link folder will be created in the same directory as the video.  It has the same name as the video, with a `.varchive` postfix. e.g. 

​	Video path: `/path/to/your-video.mp4`

​	Varchive link folder path: `/path/to/your-video.mp4.varchive`

You can also archive a network video resources (only support hls format, e.g. `m3u8`).  It won't download the entire video.

- The New folder stores new network resources you archived.

- The Recent folder stores the varchive link file of videos you watched recently.

- If you want to open a file when navigation, you can click the empty place of navigation bar where the file you want open is, then move the mouse over it and press the f on your keybord. It will open the file in your Finder app.

![bookmark-seek](https://github.com/MouJieQin/assets/blob/main/varchive/assets/bookmark-seek.mov.gif)

![bookmark-mark-seek](https://github.com/MouJieQin/assets/blob/main/varchive/assets/bookmark-mark-seek.mov.gif)

![bookmark-edit](https://github.com/MouJieQin/assets/blob/main/varchive/assets/bookmark-edit.mov.gif)

![subtitle-search](https://github.com/MouJieQin/assets/blob/main/varchive/assets/subtitle-search.mov.gif)

![video-statistic](https://github.com/MouJieQin/assets/blob/main/varchive/assets/statistic.mov.gif)
