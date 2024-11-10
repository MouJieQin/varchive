#! /usr/bin/env python3.9
# _*_coding:utf-8_*_

from __future__ import annotations
from typing import *
import datetime
import json
import asyncio


class VideoStatistics:
    def __init__(self, minClip: float = 3.0, skipThreshold: float = 1.0):
        self.minClip: float = minClip
        self.skipThreshold: float = skipThreshold
        self.currClipStart: int = -1
        self.currClipEnd: int = -1
        self.lastPos: float = -1.0
        self.timestamps = []
        self.timestampCounts = {}
        self.mergeLock = asyncio.Lock()

    def timeFormat(self, seconds: int) -> str:
        return str(datetime.timedelta(seconds=seconds))

    def dump(self, jsonPath: str):
        statistics = {
            "timestamps": self.timestamps,
            "timestampCounts": self.timestampCounts,
        }
        with open(jsonPath, mode="w", encoding="utf-8") as f:
            f.write(json.dumps(statistics, ensure_ascii=False, indent=4))

    def load(self, jsonPath: str):
        statistics = {}
        with open(jsonPath, mode="r", encoding="utf-8") as f:
            statistics = json.load(f)
        self.timestamps = statistics["timestamps"]
        self.timestampCounts = statistics["timestampCounts"]

    def __insertCount(self, timestamp: int, count: int):
        self.timestampCounts[str(timestamp)] = count

    def __getCount(self, timestamp: int):
        return self.timestampCounts[str(timestamp)]

    def __hasTimestamp(self, timestamp: int):
        return str(timestamp) in self.timestampCounts.keys()

    def __findInsertIndex(self, timestamp: int, startIndex: int, endIndex: int):
        if startIndex + 1 == endIndex:
            return startIndex if timestamp < self.timestamps[startIndex] else endIndex
        midIndex = (startIndex + endIndex) // 2
        if timestamp < self.timestamps[midIndex]:
            return self.__findInsertIndex(timestamp, startIndex, midIndex)
        else:
            return self.__findInsertIndex(timestamp, midIndex, endIndex)

    def copyClips(self, vs: VideoStatistics):
        self.timestamps = [timestamp for timestamp in vs.timestamps]
        self.timestampCounts = {}
        for key, value in vs.timestampCounts.items():
            self.timestampCounts[key] = value

    async def merge(self, vs: VideoStatistics):
        async with self.mergeLock:
            length = len(vs.timestamps)
            if length < 2:
                return
            for i in range(0, length - 1):
                self.__insertClip(
                    vs.timestamps[i],
                    vs.timestamps[i + 1],
                    vs.__getCount(vs.timestamps[i]),
                )

    def __insertClip(self, clipStartTime: int, clipEndTime: int, clipCount: int = 1):
        # print("[{},{}]".format(clipStartTime, clipEndTime))
        if clipEndTime - clipStartTime < self.minClip:
            return
        startTimePreIndex = 0
        startTimePreTimestamp = 0
        startTimePreCount = 0

        endTimePreIndex = 0
        endTimePreTimestamp = 0
        endTimePreCount = 0

        startTimeIndex = 0
        endTimeIndex = 0
        midTimestatmpsCount = 0
        if len(self.timestamps) != 0:
            startTimeIndex = self.__findInsertIndex(
                clipStartTime, 0, len(self.timestamps)
            )
            endTimeIndex = self.__findInsertIndex(clipEndTime, 0, len(self.timestamps))
            midTimestatmpsCount = endTimeIndex - startTimeIndex
        if endTimeIndex == 0:
            self.timestamps.insert(0, clipEndTime)
            self.__insertCount(clipEndTime, 0)
        else:
            endTimePreIndex = endTimeIndex - 1
            endTimePreTimestamp = self.timestamps[endTimePreIndex]
            endTimePreCount = self.__getCount(endTimePreTimestamp)
            if endTimePreTimestamp == clipEndTime:
                pass
                # do nothing
            else:
                self.timestamps.insert(endTimeIndex, clipEndTime)
                self.__insertCount(clipEndTime, endTimePreCount)

        if startTimeIndex == 0:
            self.timestamps.insert(0, clipStartTime)
            self.__insertCount(clipStartTime, clipCount)
        else:
            startTimePreIndex = startTimeIndex - 1
            startTimePreTimestamp = self.timestamps[startTimePreIndex]
            startTimePreCount = self.__getCount(startTimePreTimestamp)
            if startTimePreTimestamp == clipStartTime:
                startTimeIndex = startTimePreIndex
                self.__insertCount(clipStartTime, startTimePreCount + clipCount)
            else:
                self.timestamps.insert(startTimeIndex, clipStartTime)
                self.__insertCount(clipStartTime, startTimePreCount + clipCount)

        midTimestampsStartIndex = startTimeIndex + 1
        midTimestampsEndIndex = midTimestampsStartIndex + midTimestatmpsCount
        for index in range(midTimestampsStartIndex, midTimestampsEndIndex):
            timestamp = self.timestamps[index]
            count = self.__getCount(timestamp)
            self.__insertCount(timestamp, count + clipCount)

    def __initClip(self):
        self.currClipStart = -1
        self.currClipEnd = -1

    # this method should be called only when no more pos will be put in, such as when video is cloed.
    def forceInsert(self):
        if self.currClipStart == -1 or self.currClipEnd == -1:
            return
        self.__insertClip(self.currClipStart, self.currClipEnd)

    def put(self, currPos: float):
        timestamp = int(currPos)
        if self.currClipStart == -1:
            self.currClipStart = timestamp
            self.lastPos = currPos
            return
        if self.currClipEnd == -1:
            offset = currPos - self.lastPos
            if offset > self.skipThreshold or offset < -self.skipThreshold:
                self.__initClip()
                return
            self.currClipEnd = timestamp
            self.lastPos = currPos
            return
        offset = currPos - self.lastPos
        if offset < self.skipThreshold and offset > -self.skipThreshold:
            self.lastPos = currPos
            self.currClipEnd = timestamp
            return
        else:
            self.__insertClip(self.currClipStart, self.currClipEnd)
            self.currClipStart = timestamp
            self.currClipEnd = -1
            self.lastPos = currPos

    def getStatistics(self) -> List[Dict]:
        yAxisData = []
        seriesData = []
        totalTime = 0
        length = len(self.timestamps)
        for i in range(0, length):
            yLable = (
                self.timeFormat(self.timestamps[i])
                + "-"
                + (
                    self.timeFormat(self.timestamps[i + 1])
                    if i != length - 1
                    else "end"
                )
            )
            yAxisData.append(yLable)
            count = self.__getCount(self.timestamps[i])
            seriesData.append(count)
            if i != length - 1:
                totalTime += (self.timestamps[i + 1] - self.timestamps[i]) * count

        return {
            "timestamps": self.timestamps,
            "yAxisData": yAxisData,
            "seriesData": seriesData,
            "totalTime": self.timeFormat(totalTime),
        }
