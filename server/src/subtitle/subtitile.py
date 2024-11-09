#! /usr/bin/env python3.9
# _*_coding:utf-8_*_

import time
import json
from typing import *


class Subtitle:
    def __init__(self, subtitlePath: str):
        self.subtitlePath = subtitlePath

    def timeFormat(self, milsec: int) -> str:
        txt = time.strftime(
            "%H:%M:%S.{:0>3d}".format(milsec % 1000), time.gmtime(milsec / 1000.0)
        )
        return txt if len(txt) == 11 else txt[0:-1]

    def millisecize(self, srtTimeStr: str) -> int:
        segs = srtTimeStr.split(":")
        h = int(segs[0])
        m = int(segs[1])
        sSegs = segs[2].split(",")
        s = int(sSegs[0])
        milsec = int(sSegs[1])
        return (h * 3600 + m * 60 + s) * 1000 + milsec

    def parse(self, srtList: list) -> List[any]:
        srtListParsed = []
        srtIndex = 1
        i = 0
        while i < len(srtList) and srtList[i].strip() != str(srtIndex):
            i += 1
        while i < len(srtList):
            srtIndex += 1
            timeSegs = srtList[i + 1].split()
            startTime = self.millisecize(timeSegs[0])
            endTime = self.millisecize(timeSegs[2])
            i += 2
            txt = ""
            while i < len(srtList) and srtList[i].strip() != str(srtIndex):
                if srtList[i].strip():
                    txt += srtList[i]
                i += 1
            srtListParsed.append(
                {
                    "startTime": startTime / 1000,
                    "endTime": endTime / 1000,
                    "startTimeFormat": self.timeFormat(startTime),
                    "endTimeFormat": self.timeFormat(endTime),
                    "text": txt,
                }
            )
        return srtListParsed

    def readAndParse(self) -> List[str]:
        srtList = []
        with open(self.subtitlePath, encoding="utf-8") as fileObj:
            srtList = fileObj.readlines()
        return self.parse(srtList)

