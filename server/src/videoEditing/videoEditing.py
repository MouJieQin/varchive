from PIL import Image
import os
import time
from typing import *
from .processQueue import *
import subprocess
import multiprocessing

# from concurrent.futures import ThreadPoolExecutor
import cv2

Num_cores = multiprocessing.cpu_count()
PQueue = ProcessQueue(maxSize=1)


class VideoEditing:
    # .webp .gif
    webpFormat=".webp" 
    def __init__(self, videoPath: str, isNetworkResource: bool):
        self.videoPath: str = videoPath
        self.isNetworkResource: bool = isNetworkResource
        self.__videoDuration = -2
        self.networkResourceExt = ""

    def timeFormat(self, second: float) -> str:
        milsec = int(second * 1000)
        txt = time.strftime(
            "%H:%M:%S.{:0>3d}".format(milsec % 1000), time.gmtime(milsec / 1000.0)
        )
        return txt if len(txt) == 11 else txt[0:-1]

    def getVideoDuration(self) -> float:
        if self.__videoDuration > 0:
            return self.__videoDuration
        else:
            if not self.isNetworkResource:
                cap = cv2.VideoCapture(self.videoPath)
                if cap.isOpened():
                    rate = cap.get(5)
                    frame_num = cap.get(7)
                    duration = frame_num / rate
                    self.__videoDuration = duration
                    return duration
                return -1
            else:
                args = [
                    "ffprobe",
                    "-i",
                    self.videoPath,
                    "-show_entries",
                    "format=duration",
                    "-v",
                    "quiet",
                    "-of",
                    "csv=p=0",
                ]
                res = subprocess.run(args=args, capture_output=True, text=True)
                if res.returncode != 0:
                    print(res.stdout, res.stderr)
                    return -1
                else:
                    try:
                        self.__videoDuration = float(res.stdout)
                        print("self.__videoDuration:", self.__videoDuration)
                        return self.__videoDuration
                    except Exception as e:
                        print("Error while acquiring video duration:{}".format(e))
                        return -1

    def getNetworkResourceExt(self) -> str:
        if self.networkResourceExt != "":
            return self.networkResourceExt
        args = [
            "yt-dlp",
            "--print",
            "filename",
            "-o",
            "%(ext)s",
            self.videoPath,
        ]
        res = subprocess.run(args=args, capture_output=True, text=True)
        if res.returncode != 0:
            print(res.stderr)
            return -1
        else:
            self.networkResourceExt = res.stdout.strip()
            return self.networkResourceExt

    def getWebpPath(self, outputDir: str, startTime: float, endTime: float) -> str:
        return outputDir + "/" + str(startTime) + "-" + str(endTime) + self.webpFormat

    def getPngFilePath(self, webpFilename: str):
        return webpFilename + ".png"

    def genEscapeCharacter(self, path: str) -> str:
        path = path.replace('"', '\\"')
        return '"' + path + '"'

    def __genPreviewByTimestamps(
        self,
        outputDir: str,
        duration: float,
        timestamps: Tuple[float],
        callback: callable,
        *args,
        **kwargs
    ) -> Tuple[str]:
        webpOutputPaths: List[str] = []
        print(timestamps)
        for timestamp in timestamps:
            startTime = timestamp
            endTime = startTime + duration
            outputPath = self.getWebpPath(outputDir, startTime, endTime)
            res = self.genWebp(
                startTime, endTime, outputPath, callback, *args, **kwargs
            )
            webpOutputPaths.append(outputPath)
        return webpOutputPaths

    def genPreviewByPercentages(
        self,
        outputDir: str,
        duration: float,
        percentages: Tuple[float],
        callback: callable,
        *args,
        **kwargs
    ):
        if (
            len(percentages) == 0
            or percentages[-1] * self.getVideoDuration() + duration
            > self.getVideoDuration()
        ):
            return -1
        timestamps = [
            percentage * self.getVideoDuration() for percentage in percentages
        ]
        self.__genPreviewByTimestamps(
            outputDir, duration, timestamps, callback, *args, **kwargs
        )

    def concatWebps(self, outputPath: str, *webpFiles: str) -> Tuple[str, str]:
        frames = []
        print(webpFiles)
        try:
            for webpFile in webpFiles:
                frames.append(Image.open(webpFile))
            frames[0].save(outputPath, save_all=True, append_images=frames[1:], loop=0)
        finally:
            for frame in frames:
                frame.close()
            return self.extractFirstFrame(outputPath, outputPath + ".png")

    def extractFirstFrame(self, webpFile: str, outputPngPath: str) -> Tuple[str, str]:
        img = Image.open(webpFile)
        img.save(outputPngPath)
        return (webpFile, outputPngPath)

    def genWebp(
        self,
        startTime: float,
        endTime: float,
        outputPath: str,
        callback: callable,
        *args,
        **kwargs
    ):
        shellCmd = self.__generateWebpCmd(startTime, endTime, outputPath)
        PQueue.put(key=outputPath, command=shellCmd, callback=callback, *args, **kwargs)

    def getYtdlpOutPathNoExt(self, startTime, endTime, outputDir):
        return outputDir + "/v." + str(startTime) + "-" + str(endTime)

    def yt_dlp_DownloadSectionCmd(self, startTime, endTime, outputDir):
        startTimeFormat = self.timeFormat(startTime)
        endTimeFormat = self.timeFormat(endTime)
        timeSectionFormat = '"*' + startTimeFormat + "-" + endTimeFormat + '"'
        outputPathNoExt = self.getYtdlpOutPathNoExt(startTime, endTime, outputDir)
        args = [
            "yt-dlp",
            "--socket-timeout",
            "30",
            self.videoPath,
            "--download-sections",
            timeSectionFormat,
            "-o",
            '"' + outputPathNoExt + ".%(ext)s" + '"',
        ]
        shellCmd = " ".join(args)
        return shellCmd

    def __generateWebpCmd(
        self,
        startTime: float,
        endTime: float,
        outputPath: str,
        compression_level: int = 5,
        quality: int = 80,
        scale: str = "320:-1",
        # scale: str = "320:180",
        fps: int = 8,
        loop: int = 0,
    ) -> str:
        """
        compression_level: 0-6
        quality: 0-100
        scale: eg: iw/3:ih/3 or 1280:720
        """
        outputDir = os.path.dirname(outputPath)
        downloadSectionCmd, outputPathNoExt, videoPath = "", "", self.videoPath
        if self.isNetworkResource:
            downloadSectionCmd = self.yt_dlp_DownloadSectionCmd(
                startTime, endTime, outputDir
            )
            outputPathNoExt = self.getYtdlpOutPathNoExt(startTime, endTime, outputDir)
            videoPath = outputPathNoExt + "." + self.getNetworkResourceExt()  # ".*"
            endTime = endTime - startTime
            startTime = 0

        args = [
            "ffmpeg",
            "-i",
            self.genEscapeCharacter(videoPath),
            "-ss",
            str(startTime),
            "-to",
            str(endTime),
            "-y",
            "-v",
            "warning",
            "-threads",
            str(Num_cores - 1),
            "-loop",
            str(loop),
            "-vf",
            "fps=" + str(fps) + ",scale=" + scale,
            "-compression_level",
            str(compression_level),
            "-q:v",
            str(quality),
            self.genEscapeCharacter(outputPath),
        ]
        shellCmd = " ".join(args)
        if self.isNetworkResource:
            shellCmd = downloadSectionCmd + " && " + shellCmd + " && rm -f " + videoPath
        print("#####shellCmd:", shellCmd)
        return shellCmd
