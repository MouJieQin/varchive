#! /usr/bin/env python3.9
# _*_coding:utf-8_*_

import json
import asyncio
import os
import threading
import urllib.parse

# from queue import Queue
from .messageQueue import MessageQueue
from typing import *
from fastapi import WebSocket
import bookmarkManager.bookmarkManager as bkmarkManager
import infoManager.infoManager as infoManager
import videoStatistics.videoStatistics as videoStatistics


class WebSocketManager:
    def __init__(self, Config, maxConnection, ResourceMap, SystemRunner):
        self.ResourceMap = ResourceMap
        self.Config = Config
        self.SystemRunner = SystemRunner
        self.VideoStatisticUsing = {}
        self.maxMessage = 10
        self.spaSendInterval = 0.05
        self.maxConnection = maxConnection
        self.WebsocketIDCounter = 0
        self.getIDlock = asyncio.Lock()
        self.statisticsLock = asyncio.Lock()

        self.activeIinaConnections: list[WebSocket] = [
            None for i in range(0, self.maxConnection)
        ]

        self.activeVarchiveConnections: list[WebSocket] = [
            None for i in range(0, self.maxConnection)
        ]

        self.sendTextToIinaLocks: List[asyncio.Lock] = [
            asyncio.Lock() for i in range(0, self.maxConnection)
        ]

        self.sendTextToVarchiveLocks: List[asyncio.Lock] = [
            asyncio.Lock() for i in range(0, self.maxConnection)
        ]

        self.messagesFromIina: list[MessageQueue] = [
            MessageQueue(self.maxMessage) for i in range(0, self.maxConnection)
        ]
        self.messagesFromVarchiveVideo: list[MessageQueue] = [
            MessageQueue(self.maxMessage) for i in range(0, self.maxConnection)
        ]

        self.varchiveVIconnectInfo: list[Dict] = [
            [] for i in range(0, self.maxConnection)
        ]
        self.iinaVIconnectInfo: list[str] = ["" for i in range(0, self.maxConnection)]

        self.idMapFromIinaToVarchiveVideo: list[int] = [
            -1 for i in range(0, self.maxConnection)
        ]
        self.idMapFromVarchiveVideoToIina: list[int] = [
            -1 for i in range(0, self.maxConnection)
        ]

        self.iinaIDmapMetaPath: list[str] = ["" for i in range(0, self.maxConnection)]
        self.varchiveIDmapMetaPath: list[str] = [
            "" for i in range(0, self.maxConnection)
        ]
        self.metaFilenameMapIinaID: Dict[str : Set[int]] = {}
        self.metaFilenameMapVarchiveID: Dict[str : Set[int]] = {}

        def run_async_task():
            asyncio.run(self.VIconectionManage())

        manageVIconnectionThread = threading.Thread(target=run_async_task)
        manageVIconnectionThread.daemon = True
        manageVIconnectionThread.start()

    async def sendTextToIina(self, ID: int, text: str):
        try:
            # Acquire the lock before sending the message
            async with self.sendTextToIinaLocks[ID]:
                if self.isIinaConnected(ID):
                    await self.activeIinaConnections[ID].send_text(text)
        except Exception as e:
            print(f"An error occurred while sending text to IINA[{ID}]: {e}")

    async def sendTextToVarchive(self, ID: int, text: str):
        try:
            # Acquire the lock before sending the message
            async with self.sendTextToVarchiveLocks[ID]:
                if self.isVarchiveConnected(ID):
                    await self.activeVarchiveConnections[ID].send_text(text)
        except Exception as e:
            print(f"An error occurred while sending text to Varchive[{ID}]: {e}")

    async def broadcastToIinasByMetaPath(self, metaPath: str, text: str):
        try:
            if metaPath not in self.metaFilenameMapIinaID.keys():
                return
            for id in self.metaFilenameMapIinaID[metaPath]:
                await self.sendTextToIina(id, text)
        except Exception as e:
            print(f"An error occurred when broadcast to iinas: {e}")

    async def broadcastToVarchivesByMetaPath(self, metaPath: str, text: str):
        try:
            if metaPath not in self.metaFilenameMapVarchiveID.keys():
                return
            for id in self.metaFilenameMapVarchiveID[metaPath]:
                await self.sendTextToVarchive(id, text)
        except Exception as e:
            print(f"An error occurred when broadcast to varchives: {e}")

    async def broadcastToIinasByIinaID(self, ID: int, text: str):
        metaPath = self.iinaIDmapMetaPath[ID]
        await self.broadcastToIinasByMetaPath(metaPath, text)

    async def broadcastToVarchivesByIinaID(self, ID: int, text: str):
        metaPath = self.iinaIDmapMetaPath[ID]
        await self.broadcastToVarchivesByMetaPath(metaPath, text)

    async def broadcastToIinasByVarchiveID(self, ID: int, text: str):
        metaPath = self.varchiveIDmapMetaPath[ID]
        await self.broadcastToIinasByMetaPath(metaPath, text)

    async def broadcastToVarchivesByVarchiveID(self, ID: int, text: str):
        metaPath = self.varchiveIDmapMetaPath[ID]
        await self.broadcastToVarchivesByMetaPath(metaPath, text)

    async def broadcastToAllByMetaPath(self, metaPath: str, text: str):
        await self.broadcastToIinasByMetaPath(metaPath, text)
        await self.broadcastToVarchivesByMetaPath(metaPath, text)

    async def broadcastToAllByIinaID(self, ID: int, text: str):
        metaPath = self.iinaIDmapMetaPath[ID]
        await self.broadcastToAllByMetaPath(metaPath, text)

    async def broadcastToAllByVarchiveID(self, ID: int, text: str):
        metaPath = self.varchiveIDmapMetaPath[ID]
        await self.broadcastToAllByMetaPath(metaPath, text)

    async def getIDAvailableForVarchive(self) -> int:
        async with self.getIDlock:
            if self.WebsocketIDCounter >= self.maxConnection:
                self.WebsocketIDCounter = 0
            self.WebsocketIDCounter += 1
            for ID in range(self.WebsocketIDCounter, self.maxConnection):
                if not self.isVarchiveConnected(ID):
                    self.WebsocketIDCounter = ID
                    return ID
            for ID in range(1, self.WebsocketIDCounter):
                if not self.isVarchiveConnected(ID):
                    self.WebsocketIDCounter = ID
                    return ID
            return -1

    async def VIconectionManage(self):
        while True:
            for i in range(0, self.maxConnection):
                #  This IINA ID is waiting to connect to varchive
                if (
                    self.isIinaConnected(i)
                    and self.idMapFromIinaToVarchiveVideo[i] == -1
                ):
                    if self.iinaVIconnectInfo[i] != "":
                        # print("looking peer:", self.iinaVIconnectInfo[i])
                        for j in range(0, self.maxConnection):
                            #  This varchive ID is waiting to connect to iina
                            if (
                                self.isVarchiveConnected(j)
                                and self.idMapFromVarchiveVideoToIina[j] == -1
                            ):
                                if self.varchiveVIconnectInfo[j] != []:
                                    # print("Urls:", self.varchiveVIconnectInfo[j])
                                    for url in self.varchiveVIconnectInfo[j]:
                                        # Avoiding repeated connection with multiple varchive ID that is related to the smae video
                                        # note: this IINA ID may have connected with the previous varchive ID in this for loop.
                                        if self.idMapFromIinaToVarchiveVideo[i] == -1:
                                            if self.iinaVIconnectInfo[
                                                i
                                            ] == urllib.parse.unquote(url):
                                                print(
                                                    "@@@@@@@@@@@@@@@@@@@@@@@@ The connection between iina and varchive successfully: IINA[{}] Varchive[{}]".format(
                                                        i, j
                                                    )
                                                )
                                                await self.setIDMap(i, j)
            await self.sleep()

    async def sleep(self):
        await asyncio.sleep(self.spaSendInterval)

    async def connectIina(self, ID: int, websocket: WebSocket):
        await websocket.accept()
        self.activeIinaConnections[ID] = websocket
        print(
            "WebSocketManager: The connection whose ID is [{}] from [IINA] open.".format(
                ID
            )
        )

    async def connectVarchive(self, ID: int, websocket: WebSocket):
        await websocket.accept()
        self.activeVarchiveConnections[ID] = websocket
        print(
            "WebSocketManager: The connection whose ID is [{}] from [Varchive] open.".format(
                ID
            )
        )

    async def updateVideoStatisticsWhenDisconnnect(self, ID: int, currentURL: str):
        metaPath = self.ResourceMap.getMetaPathByURL(currentURL)
        if not metaPath or not os.path.exists(metaPath):
            return
        statisticsPath = self.ResourceMap.getStatisticsPathByMetaPath(metaPath)
        orginal: videoStatistics.VideoStatistics = self.VideoStatisticUsing[
            statisticsPath
        ]["orginal"]
        vsID: videoStatistics.VideoStatistics = self.VideoStatisticUsing[
            statisticsPath
        ][str(ID)]
        vsID.forceInsert()
        await orginal.merge(vsID)
        self.VideoStatisticUsing[statisticsPath].pop(str(ID))
        self.VideoStatisticUsing[statisticsPath].pop(self.__getKeyOfVsForVarchive(ID))
        metaPath = self.ResourceMap.getMetaPathByURL(currentURL)
        orginal.dump(statisticsPath)
        if len(self.VideoStatisticUsing[statisticsPath]) == 1:
            self.VideoStatisticUsing.pop(statisticsPath)

    async def disconnectIina(self, ID: int):
        await self.updateVideoStatisticsWhenDisconnnect(ID, self.iinaVIconnectInfo[ID])
        self.activeIinaConnections[ID] = None
        self.iinaVIconnectInfo[ID] = ""
        if self.iinaIDmapMetaPath[ID]:
            self.metaFilenameMapIinaID[self.iinaIDmapMetaPath[ID]].discard(ID)
        self.iinaIDmapMetaPath[ID] = ""
        varchiveVideoID = self.idMapFromIinaToVarchiveVideo[ID]
        self.clearIDMap(ID, varchiveVideoID)
        print(
            "WebSocketManager: The connection whose ID is [{}] from [IINA] closed.".format(
                ID
            )
        )

    def disconnectVarchive(self, ID: int):
        self.activeVarchiveConnections[ID] = None
        self.varchiveVIconnectInfo[ID] = []
        if self.varchiveIDmapMetaPath[ID]:
            self.metaFilenameMapVarchiveID[self.varchiveIDmapMetaPath[ID]].discard(ID)
        self.varchiveIDmapMetaPath[ID] = ""
        iinaID = self.idMapFromVarchiveVideoToIina[ID]
        self.clearIDMap(iinaID, ID)
        print(
            "WebSocketManager: The connection whose ID is [{}] from [Varchive] closed.".format(
                ID
            )
        )

    def isIinaConnected(self, ID: int):
        return self.activeIinaConnections[ID] is not None

    def isVarchiveConnected(self, ID: int):
        return self.activeVarchiveConnections[ID] is not None

    async def sendPairedInfo(self, iinaID: int, varchiveVideoID: int):
        info = {
            "type": ["varchive", "connection", "paired"],
            "message": "",
        }
        await self.sendTextToVarchive(varchiveVideoID, json.dumps(info))

    async def sendDispairedInfoToVarchiveByIinaID(self, iinaID: int):
        info = {
            "type": ["varchive", "connection", "dispaired"],
            "message": "",
        }
        varchiveVideoID = self.idMapFromIinaToVarchiveVideo[iinaID]
        if varchiveVideoID == -1 or not self.activeVarchiveConnections[varchiveVideoID]:
            return
        await self.sendTextToVarchive(varchiveVideoID, json.dumps(info))

    async def setIDMap(self, iinaID: int, varchiveVideoID: int):
        self.idMapFromIinaToVarchiveVideo[iinaID] = varchiveVideoID
        self.idMapFromVarchiveVideoToIina[varchiveVideoID] = iinaID
        await self.sendPairedInfo(iinaID, varchiveVideoID)

    def clearIDMap(self, iinaID: int, varchiveVideoID: int):
        self.idMapFromIinaToVarchiveVideo[iinaID] = -1
        self.idMapFromVarchiveVideoToIina[varchiveVideoID] = -1

    def __getKeyOfVsForVarchive(self, ID: int):
        return str(ID) + "forVarchive"

    async def prepareDataForVideoStatistics(self, ID: int, currentURL: str):
        async with self.statisticsLock:
            metaPath = self.ResourceMap.getMetaPathByURL(currentURL)
            if not metaPath or not os.path.exists(metaPath):
                return
            statisticsPath = self.ResourceMap.getStatisticsPathByMetaPath(metaPath)
            if statisticsPath not in self.VideoStatisticUsing.keys():
                vs = videoStatistics.VideoStatistics()
                if os.path.exists(statisticsPath):
                    vs.load(statisticsPath)
                self.VideoStatisticUsing[statisticsPath] = {"orginal": vs}

            vs = videoStatistics.VideoStatistics()
            vsForVarchive = videoStatistics.VideoStatistics()
            vsForVarchive.copyClips(self.VideoStatisticUsing[statisticsPath]["orginal"])
            self.VideoStatisticUsing[statisticsPath][str(ID)] = vs
            self.VideoStatisticUsing[statisticsPath][
                self.__getKeyOfVsForVarchive(ID)
            ] = vsForVarchive

    async def handleMessageFromIINA(
        self, ID: int, text: str, messages: MessageQueue, websocket: WebSocket
    ):
        messageJson = json.loads(text)
        firstType = messageJson["type"][0]
        if firstType == "varchive":
            if messageJson["type"][1] == "playerInfo":
                message = json.loads(messageJson["message"])
                currentURL = message["currentURL"]
                metaPath = self.ResourceMap.getMetaPathByURL(currentURL)
                if (not metaPath) or (not os.path.exists(metaPath)):
                    videoStatisticser = videoStatistics.VideoStatistics()
                    messageJson["statistics"] = videoStatisticser.getStatistics()
                    messages.put(json.dumps(messageJson))
                else:
                    self.iinaIDmapMetaPath[ID] = metaPath
                    if metaPath not in self.metaFilenameMapIinaID.keys():
                        self.metaFilenameMapIinaID[metaPath] = {ID}
                    else:
                        self.metaFilenameMapIinaID[metaPath].add(ID)
                    statisticsPath = self.ResourceMap.getStatisticsPathByMetaPath(
                        metaPath
                    )
                    if statisticsPath not in self.VideoStatisticUsing.keys():
                        await self.prepareDataForVideoStatistics(ID, currentURL)
                    if str(ID) not in self.VideoStatisticUsing[statisticsPath].keys():
                        await self.prepareDataForVideoStatistics(ID, currentURL)
                    videoStatisticser = self.VideoStatisticUsing[statisticsPath][
                        str(ID)
                    ]
                    videoStatisticserForVarchive = self.VideoStatisticUsing[
                        statisticsPath
                    ][self.__getKeyOfVsForVarchive(ID)]
                    pos = message["pos"]
                    videoStatisticser.put(pos)
                    videoStatisticserForVarchive.put(pos)
                    statistics = videoStatisticserForVarchive.getStatistics()
                    messageJson["statistics"] = statistics
                    messages.put(json.dumps(messageJson))
            else:
                messages.put(text)
        elif firstType == "server":
            secondType = messageJson["type"][1]
            if secondType == "connection":
                currentURL = json.loads(messageJson["message"])["currentURL"]
                self.iinaVIconnectInfo[ID] = currentURL
                self.ResourceMap.pushRecentByURL(currentURL)
            else:
                message = json.loads(messageJson["message"])
                currentURL = message["currentURL"]
                metaPath = self.ResourceMap.getMetaPathByURL(currentURL)
                informationManager = infoManager.IINAinfoManager(
                    messageJson["type"],
                    messageJson["message"],
                    lambda text: self.sendTextToIina(ID, text),
                    lambda text: self.broadcastToIinasByMetaPath(metaPath, text),
                    lambda text: self.broadcastToVarchivesByMetaPath(metaPath, text),
                    messages,
                    self.ResourceMap,
                )
                await informationManager.handleMessage()
        else:
            # Never happen
            pass

    async def handleMessageFromVarchive(
        self, ID: int, text: str, messages: MessageQueue, websocket: WebSocket
    ):
        print(text)
        messageJson = json.loads(text)
        firstType = messageJson["type"][0]
        if firstType == "iina":
            secondType = messageJson["type"][1]
            if secondType == "seek":
                if self.idMapFromVarchiveVideoToIina[ID] == -1:
                    self.openInIina(ID, messageJson["type"][2])
            messages.put(text)
        elif firstType == "server":
            secondType = messageJson["type"][1]
            if secondType == "connection":
                self.varchiveVIconnectInfo[ID] = json.loads(messageJson["message"])
                varchiveCurrentPath = messageJson["type"][2]
                metaPath = self.ResourceMap.getMetaPathByVarchiveCurrentPath(
                    varchiveCurrentPath
                )
                self.varchiveIDmapMetaPath[ID] = metaPath
                if metaPath not in self.metaFilenameMapVarchiveID.keys():
                    self.metaFilenameMapVarchiveID[metaPath] = {ID}
                else:
                    self.metaFilenameMapVarchiveID[metaPath].add(ID)
            elif secondType == "openInIINA":
                self.openInIina(ID, messageJson["message"])
            else:
                message = json.loads(messageJson["message"])
                varchiveCurrentPath = message["varchiveCurrentPath"]
                metaPath = self.ResourceMap.getMetaPathByVarchiveCurrentPath(
                    varchiveCurrentPath
                )
                informationManager = infoManager.VarchiveInfoManager(
                    messageJson["type"],
                    messageJson["message"],
                    lambda text: self.sendTextToVarchive(ID, text),
                    lambda text: self.broadcastToIinasByMetaPath(metaPath, text),
                    lambda text: self.broadcastToVarchivesByMetaPath(metaPath, text),
                    messages,
                    self.ResourceMap,
                )
                await informationManager.handleMessage()
        else:
            pass

    async def receiveMessageFromIina(self, iinaID: int, websocket: WebSocket):
        messages = self.messagesFromIina[iinaID]
        while self.isIinaConnected(iinaID):
            text = await websocket.receive_text()
            await self.handleMessageFromIINA(iinaID, text, messages, websocket)

    async def receiveMessageFromVarchiveVideoDetails(
        self, varchiveVideoID: int, websocket: WebSocket
    ):
        messages = self.messagesFromVarchiveVideo[varchiveVideoID]
        while self.isVarchiveConnected(varchiveVideoID):
            text = await websocket.receive_text()
            await self.handleMessageFromVarchive(
                varchiveVideoID, text, messages, websocket
            )

    async def sendMessageToIina(self, iinaID: int, websocket: WebSocket):
        while self.isIinaConnected(iinaID):
            while self.idMapFromIinaToVarchiveVideo[iinaID] == -1:
                await self.sleep()
            varchiveVideoID = self.idMapFromIinaToVarchiveVideo[iinaID]
            messages = self.messagesFromVarchiveVideo[varchiveVideoID]
            if not messages.empty():
                message = messages.get()
                try:
                    await self.sendTextToIina(iinaID, message)
                except Exception as e:
                    print(
                        "This exception may be normal because the connection to IINA is closed.{}".format(
                            e
                        )
                    )
                    self.disconnectVarchive(iinaID)
            else:
                await self.sleep()

    async def sendMessageToVarchiveVideoDetails(
        self, varchiveVideoID: int, websocket: WebSocket
    ):
        while self.isVarchiveConnected(varchiveVideoID):
            while self.idMapFromVarchiveVideoToIina[varchiveVideoID] == -1:
                await self.sleep()
            iinaID = self.idMapFromVarchiveVideoToIina[varchiveVideoID]
            messages = self.messagesFromIina[iinaID]
            if not messages.empty():
                message = messages.get()
                try:
                    await self.sendTextToVarchive(varchiveVideoID, message)
                except Exception as e:
                    print(
                        "This exception may be normal because the connection to varchive is closed.{}".format(
                            e
                        )
                    )
                    self.disconnectVarchive(varchiveVideoID)
            else:
                await self.sleep()

    async def __callbackForOpenInIina(self, res, ID: int):
        if res.returncode == 0:
            message = infoManager.VarchiveInfoManager.genNotificationMessageForVarchive(
                "message", "success", "Opened in iina.", ""
            )
            await self.sendTextToVarchive(ID, message)
        else:
            print(res.stderr)
            message = infoManager.VarchiveInfoManager.genNotificationMessageForVarchive(
                "notification", "error", "Error while opening it in iina.", res.stderr
            )
            await self.sendTextToVarchive(ID, message)

    def openInIina(self, ID: int, url: str) -> str:
        iinaPath = self.Config["iina"]["path"]
        command = ["open", url, "-a", iinaPath]
        print(command)
        self.SystemRunner.put(command, self.__callbackForOpenInIina, ID)
        return ""
