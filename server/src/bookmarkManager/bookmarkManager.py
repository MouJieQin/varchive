#! /usr/bin/env python3.9
# _*_coding:utf-8_*_

import json
from typing import *
import os
import time

import videoEditing.videoEditing as videoEditing
import webSocketManager.messageQueue as messageQueue
from resourceMap.resourceMap import ResourceMapManager
from videoEditing.processQueue import *
from threadAsync.threadAsync import ThreadAsync

#  Store used bookmark.json to avoid overwriting bookmark.json while multiple running async bookmark operations (eg. insert) are performing
BookmarksUsing = {}


class BookmarkManager:
    threadAsync = ThreadAsync()

    def __init__(
        self,
        type: List[str],
        message: str,
        # ientify: str,
        sendText: Callable,
        broadcastToIinas: Callable,
        broadcastToVarchives: Callable,
        putMessageToBroadcastVarchives: Callable,
        messageQueue: messageQueue.MessageQueue,
        ResourceMap: ResourceMapManager,
    ):
        self.type = type
        self.message = json.loads(message)
        # self.ientify = ientify
        self.sendText = sendText
        self.broadcastToIinas = broadcastToIinas
        self.broadcastToVarchives = broadcastToVarchives
        self.putMessageToBroadcastVarchives = putMessageToBroadcastVarchives
        self.isWebsocketClosed = False
        self.messageQueue = messageQueue
        self.ResourceMap = ResourceMap
        self.url = self.message["currentURL"]
        self.isNetworkResource = False
        self.duration = 3
        self.urlForEditing = self.url
        self.varchiveLinkDir = ""
        self.varchiveDir = ""
        self.webpsDir = ""
        self.bookmarkJson = {"path": self.url, "bookmarks": []}
        self.bookmarkPath = ""
        self.detailsPath = ""
        self.fileName = os.path.basename(self.url)
        self.__initData()
        self.infoJson = {
            "path": [
                {
                    "url": self.url,
                    "isSelected": True,
                }
            ],
            "fileName": self.fileName,
            "title": os.path.splitext(self.fileName)[0],
            "description": "",
            "cover": {
                "webp": "/icons/landscape.png",
                "cover": "/icons/landscape.png",
                "startTime": 0,
                "endTime": 0,
            },
            "previews": {"clips": []},
            "info": "",
        }

    @staticmethod
    def genNotificationMessageForVarchive(
        boxType: str, type: str, title: str, description: str
    ):
        note = {
            "boxType": boxType,
            "type": type,
            "title": title,
            "description": description,
        }
        message = {"type": ["varchive", "notification"], "message": json.dumps(note)}
        return json.dumps(message)

    @staticmethod
    def genNotificationMessageForIina(
        type: str, currentURL: str, title: str, description: str, timeout: float
    ):
        message = {
            "currentURL": currentURL,
            "type": type,
            "title": title,
            "description": description,
            "timeout": timeout,
        }
        notificationMessage = {
            "type": ["iina", "notification"],
            "message": json.dumps(message),
        }
        return json.dumps(notificationMessage)

    def _syncInfoToFile(self):
        with open(self.detailsPath, mode="w", encoding="utf-8") as f:
            f.write(json.dumps(self.infoJson, ensure_ascii=False, indent=4))

    async def _sendDetailsMessageForVarchive(
        self, type: str, isBroadcast: bool = False
    ):
        detailsInfo = {
            "type": ["varchive", "details", type],
            "message": json.dumps(self.infoJson),
        }
        try:
            if isBroadcast:
                await self.broadcastToVarchives(json.dumps(detailsInfo))
            else:
                if not self.isWebsocketClosed:
                    await self.sendText(json.dumps(detailsInfo))
        except Exception as e:
            self.isWebsocketClosed = True
            print(
                "This exception may be normal because the connection to varchive have been closed. {}".format(
                    e
                )
            )

    def _putMessageToBroadcastDetailsMessageToVarchives(self, type: str):
        detailsInfo = {
            "type": ["varchive", "details", type],
            "message": json.dumps(self.infoJson),
        }
        self.putMessageToBroadcastVarchives(json.dumps(detailsInfo))

    def _syncInformation(self):
        self._syncInfoToFile()
        self._putMessageToBroadcastDetailsMessageToVarchives("info")

    def _initDetails(self):
        linkPath = ""
        if not self.isNetworkResource:
            linkPath = self.varchiveLinkDir
        self.varchiveDir = self.ResourceMap.createMetaPath(self.url, linkPath)
        self.detailsPath = self.ResourceMap.getDetailsPath(self.varchiveDir)
        self.bookmarkPath = self.ResourceMap.getBookmarkPath(self.varchiveDir)
        self.webpsDir = self.ResourceMap.getWebpsPath(self.varchiveDir)
        with open(self.detailsPath, mode="w", encoding="utf-8") as f:
            f.write(json.dumps(self.infoJson, ensure_ascii=False, indent=4))
        self.ResourceMap.pushRecentByURL(self.url)

    def timeFormat(self, second: float) -> str:
        milsec = int(second * 1000)
        txt = time.strftime(
            "%H:%M:%S.{:0>3d}".format(milsec % 1000), time.gmtime(milsec / 1000.0)
        )
        return txt if len(txt) == 11 else txt[0:-1]

    def __initData(self):
        (self.isNetworkResource, self.urlForEditing) = self.ResourceMap.parseURL(
            self.url
        )
        if not self.isNetworkResource:
            if "varchiveCurrentPath" in self.message.keys():
                # This is a varchive manager instance.
                self.varchiveLinkDir = self.ResourceMap.getLinkDirByVarchiveCurrentPath(
                    self.message["varchiveCurrentPath"]
                )
            else:
                self.varchiveLinkDir = self.ResourceMap.getLinkDirByLocalPath(
                    self.urlForEditing
                )
            if os.path.exists(self.varchiveLinkDir):
                self.varchiveDir = self.ResourceMap.getMetaPathByLinkDir(
                    self.varchiveLinkDir
                )
                self.webpsDir = self.ResourceMap.getWebpsPath(self.varchiveDir)
                self.detailsPath = self.ResourceMap.getDetailsPath(self.varchiveDir)
                self.bookmarkPath = self.ResourceMap.getBookmarkPath(self.varchiveDir)
                if os.path.exists(self.bookmarkPath):
                    if self.bookmarkPath in BookmarksUsing.keys():
                        self.bookmarkJson = BookmarksUsing[self.bookmarkPath]
                    else:
                        with open(self.bookmarkPath, mode="r", encoding="utf-8") as f:
                            BookmarksUsing[self.bookmarkPath] = json.load(f)
                        self.bookmarkJson = BookmarksUsing[self.bookmarkPath]
            else:
                pass
        else:
            if self.ResourceMap.hasKey(self.url):
                self.varchiveDir = self.ResourceMap.keyMapPath(self.url)
                self.webpsDir = self.ResourceMap.getWebpsPath(self.varchiveDir)
                self.detailsPath = self.ResourceMap.getDetailsPath(self.varchiveDir)
                self.bookmarkPath = self.ResourceMap.getBookmarkPath(self.varchiveDir)
                if os.path.exists(self.bookmarkPath):
                    if self.bookmarkPath in BookmarksUsing.keys():
                        self.bookmarkJson = BookmarksUsing[self.bookmarkPath]
                    else:
                        with open(self.bookmarkPath, mode="r", encoding="utf-8") as f:
                            BookmarksUsing[self.bookmarkPath] = json.load(f)
                        self.bookmarkJson = BookmarksUsing[self.bookmarkPath]
            else:
                pass

    def _removeFile(self, path: str):
        if os.path.isfile(path):
            os.remove(path)

    def _cancelClip(self, clip: Dict):
        webpPath = self._getWebpPath(
            self.webpsDir,
            clip["startTime"],
            clip["endTime"],
        )
        videoEditing.PQueue.cancel(key=webpPath)

    def _cancelBookmark(self, bookmark: Dict):
        self._cancelClip(bookmark["clip"])

    def _getPngFilePath(self, webpFilename: str):
        return webpFilename + ".png"

    def _getWebpPath(self, outputDir: str, startTime: float, endTime: float) -> str:
        return (
            outputDir
            + "/"
            + str(startTime)
            + "-"
            + str(endTime)
            + videoEditing.VideoEditing.webpFormat
        )

    def _createWebpDirIfNotExist(self):
        if not os.path.exists(self.webpsDir):
            os.makedirs(self.webpsDir)

    def _syncBookmarksToFile(self):
        with open(self.bookmarkPath, mode="w", encoding="utf-8") as f:
            f.write(json.dumps(self.bookmarkJson, ensure_ascii=False, indent=4))

    def _removeClipFiles(self, clip: Dict):
        webpPath = self._getWebpPath(self.webpsDir, clip["startTime"], clip["endTime"])
        png = self._getPngFilePath(webpPath)
        self._removeFile(webpPath)
        self._removeFile(png)

    def _removeFilesAboutBookmark(self, bookmark: Dict):
        self._removeClipFiles(bookmark["clip"])

    def __changeImg(self, clip: Dict, webp: str, png: str, syncVarchive: Callable):
        clip["webp"] = webp
        clip["cover"] = png
        syncVarchive()

    def __changeImgWhileReady(self, clip: Dict, syncVarchive: Callable):
        self.__changeImg(
            clip, "/icons/infinity.webp", "/icons/infinity.webp", syncVarchive
        )

    def __changeImgWhileRunning(self, clip: Dict, syncVarchive: Callable):
        self.__changeImg(
            clip, "/icons/loading.webp", "/icons/loading.webp", syncVarchive
        )

    def __changeImgWhenCancedOrFailed(self, clip: Dict, syncVarchive: Callable):
        self.__changeImg(
            clip, "/icons/landscape.png", "/icons/landscape.png", syncVarchive
        )

    def _changeImgWhileDone(
        self, clip: Dict, webp: str, png: str, syncVarchive: Callable
    ):
        self.__changeImg(clip, webp, png, syncVarchive)

    def __getRelativeWebpPngPath(self, outputPath: str) -> List[str]:
        webpFileName = os.path.basename(outputPath)
        webpRelativePath = "webps/" + webpFileName
        pngRelativePath = webpRelativePath + ".png"
        return (webpRelativePath, pngRelativePath)

    def _genWebpCallback(
        self,
        status: TaskStatus,
        outPath: str,
        clip: Dict,
        VEditor: videoEditing.VideoEditing,
        syncVarchive: Callable,
        isPreview: bool,
        previewWebpOutputPaths: Tuple[str],
        previewWebpCoverPath: str,
        cover: Dict,
    ):
        try:
            if status == TaskStatus.READY:
                self.__changeImgWhileReady(clip, syncVarchive)
                print("TaskStatus.READY:", outPath)
            elif status == TaskStatus.CANCELED:
                self._removeFile(outPath)
                self.__changeImgWhenCancedOrFailed(clip, syncVarchive)
                print("TaskStatus.CANCELED:", outPath)
            elif status == TaskStatus.RUNNING:
                print("TaskStatus.RUNNING:", outPath)
                self.__changeImgWhileRunning(clip, syncVarchive)
            elif status == TaskStatus.FAILED:
                self._removeFile(outPath)
                self.__changeImgWhenCancedOrFailed(clip, syncVarchive)
                print("TaskStatus.FAILED:", outPath)
            elif status == TaskStatus.DONE:
                print("TaskStatus.DONE:", outPath)
                VEditor.extractFirstFrame(outPath, self._getPngFilePath(outPath))
                (webpRelativePath, pngRelativePath) = self.__getRelativeWebpPngPath(
                    outPath
                )
                self._changeImgWhileDone(
                    clip, webpRelativePath, pngRelativePath, syncVarchive
                )
                # It will coverwrite the cover, disable it currently.
                # if isPreview:
                #     previewWebpOutputPaths.append(outPath)
                #     VEditor.concatWebps(previewWebpCoverPath, *previewWebpOutputPaths)
                #     (webpRelativePath, pngRelativePath) = self.__getRelativeWebpPngPath(
                #         previewWebpCoverPath
                #     )
                #     self._changeImgWhileDone(
                #         cover, webpRelativePath, pngRelativePath, syncVarchive
                #     )
            else:
                pass
        except Exception as e:
            print(
                "This exception may be normal because files have been deleted.{}".format(
                    e
                )
            )

    # bookmark

    def _genBookmarkInfoForIINA(self) -> str:
        timestampInfo = self.bookmarkJson["bookmarks"]
        timestamps = []
        titles = []
        descriptions = []
        for info in timestampInfo:
            timestamps.append(info["timestamp"])
            titles.append(info["title"])
            descriptions.append(info["description"])
        return json.dumps(
            {
                "currentURL": self.url,
                "timestamps": timestamps,
                "titles": titles,
                "descriptions": descriptions,
            }
        )

    async def _broadcastBookmarkInfoToVarchives(self):
        bookmarkInfo = {
            "type": ["varchive", "bookmarks", "info"],
            "message": json.dumps(self.bookmarkJson),
        }
        await self.broadcastToVarchives(json.dumps(bookmarkInfo))

    def _putMessageToBroadcastBookmarkInfoToVarchives(self):
        bookmarkInfo = {
            "type": ["varchive", "bookmarks", "info"],
            "message": json.dumps(self.bookmarkJson),
        }
        self.putMessageToBroadcastVarchives(json.dumps(bookmarkInfo))

    async def _sendMessageToVarchives(self, infoType: str):
        bookmarkInfo = {
            "type": ["varchive", "bookmarks", infoType],
            "message": json.dumps(self.bookmarkJson),
        }
        await self.broadcastToVarchives(json.dumps(bookmarkInfo))

    def __iinaRemoveMessage(self, currentURL: str, index: int, timestamp: float):
        removeBookmarkInfo = {
            "currentURL": currentURL,
            "index": index,
            "timestamp": timestamp,
        }
        message = json.dumps(removeBookmarkInfo)
        websocketMessage = {
            "type": ["iina", "bookmarks", "remove"],
            "message": message,
        }
        return json.dumps(websocketMessage)

    async def _handleRemove(self, peer: str):
        print(
            "BookmarkManager: received [Remove] bookmark requirement for ",
            self.message["currentURL"],
            "\ntimestamp:",
            self.message["timestamp"],
            "\nindex:",
            self.message["index"],
        )
        currentURL = self.message["currentURL"]
        index = self.message["index"]
        timestamp = self.message["timestamp"]
        bookmarks = self.bookmarkJson["bookmarks"]
        if index < len(bookmarks) and bookmarks[index]["timestamp"] == timestamp:
            # Cancel the running insert bookmark operation
            self._cancelBookmark(bookmarks[index])
            self._removeFilesAboutBookmark(bookmarks[index])
            bookmarks.pop(index)
            self._syncBookmarksToFile()
        else:
            me = "iina" if peer == "varchive" else "varchive"
            websocketMessage = {
                "type": [me, "bookmarks", "remove-error"],
                "message": "Index [{}] is not consistent to timestamp [{}]. bookmarks had already changed before you submited".format(
                    index, timestamp
                ),
            }
            await self.sendText(json.dumps(websocketMessage))
            return

        # notify iina
        removeMessageForIina = self.__iinaRemoveMessage(currentURL, index, timestamp)
        await self.broadcastToIinas(removeMessageForIina)
        # notify varchive
        await self._sendMessageToVarchives("removed")

    async def _handleClear(self, peer: str):
        print(
            "BookmarkManager: received [Clear] bookmark requirement for ",
            self.message["currentURL"],
        )
        currentURL = self.message["currentURL"]
        for bookmark in self.bookmarkJson["bookmarks"]:
            # Cancel running insert bookmark operations
            self._cancelBookmark(bookmark)
            self._removeFilesAboutBookmark(bookmark)
        self.bookmarkJson["bookmarks"] = []
        self._syncBookmarksToFile()

        # notify iina
        clearMessage = json.dumps(
            {
                "currentURL": currentURL,
            }
        )
        websocketMessage = {
            "type": [peer, "bookmarks", "clear"],
            "message": clearMessage,
        }
        await self.broadcastToIinas(json.dumps(websocketMessage))
        # notify varchive
        await self._sendMessageToVarchives("cleared")


class IINAbookmarkManager(BookmarkManager):
    def __init__(
        self,
        type: List[str],
        message: str,
        sendText: Callable,
        broadcastToIinas: Callable,
        broadcastToVarchives: Callable,
        putMessageToBroadcastVarchives: Callable,
        messageQueue: messageQueue.MessageQueue,
        ResourceMap: ResourceMapManager,
    ):
        super().__init__(
            type,
            message,
            sendText,
            broadcastToIinas,
            broadcastToVarchives,
            putMessageToBroadcastVarchives,
            messageQueue,
            ResourceMap,
        )

    def __createBookmarkJsonFileIfNotExist(self):
        if self.isNetworkResource and not self.ResourceMap.hasKey(self.url):
            self._initDetails()
        if not self.isNetworkResource and not self.ResourceMap.isVarchiveVideoLink(
            self.varchiveLinkDir
        ):
            self._initDetails()
        if not os.path.exists(self.bookmarkPath):
            if not os.path.exists(self.varchiveDir):
                os.makedirs(self.varchiveDir)
            BookmarksUsing[self.bookmarkPath] = self.bookmarkJson
            self._syncBookmarksToFile()

    def _syncBookmarks(self):
        self._syncBookmarksToFile()
        self._putMessageToBroadcastBookmarkInfoToVarchives()

    async def __handleFetch(self):
        print(
            "BookmarkManager: received [Fetch] bookmarks requirement for ",
            self.message["currentURL"],
        )
        bookmarkInfo = {
            "type": ["iina", "bookmarks", "info"],
            "message": self._genBookmarkInfoForIINA(),
        }
        await self.sendText(json.dumps(bookmarkInfo))

    async def __handleInsert(self):
        self.__createBookmarkJsonFileIfNotExist()
        currentURL = self.message["currentURL"]
        index = self.message["index"]
        timestamp = self.message["timestamp"]
        print(
            "BookmarkManager: received [Insert] bookmark requirement for ",
            currentURL,
            "\ntimestamp:",
            timestamp,
            "\nindex:",
            index,
        )
        startTime = timestamp
        endTime = startTime + self.duration
        newBookmark = {
            "timestamp": timestamp,
            "format": self.timeFormat(timestamp),
            "title": "The marked timestamp",
            "description": "No description.",
            "clip": {
                "webp": "/icons/landscape.png",
                "cover": "/icons/landscape.png",
                "startTime": startTime,
                "endTime": endTime,
            },
        }
        self.bookmarkJson["bookmarks"].insert(index, newBookmark)
        self._syncBookmarksToFile()
        await self._broadcastBookmarkInfoToVarchives()
        insertBookmarkInfo = {
            "currentURL": currentURL,
            "index": index,
            "timestamp": timestamp,
            "title": newBookmark["title"],
            "description": newBookmark["description"],
        }
        message = json.dumps(insertBookmarkInfo)
        websocketMessage = {
            "type": ["iina", "bookmarks", "insert"],
            "message": message,
        }
        await self.broadcastToIinas(json.dumps(websocketMessage))

        if self.type[3] == "mark-preview":
            self._createWebpDirIfNotExist()
            videoEditor = videoEditing.VideoEditing(
                self.urlForEditing, self.isNetworkResource
            )
            outputPath = self._getWebpPath(self.webpsDir, startTime, endTime)
            videoEditor.genWebp(
                startTime,
                endTime,
                outputPath,
                self._genWebpCallback,
                outPath=outputPath,
                clip=newBookmark["clip"],
                VEditor=videoEditor,
                syncVarchive=self._syncBookmarks,
                isPreview=False,
                previewWebpOutputPaths=[],
                previewWebpCoverPath="",
                cover={},
            )

    async def handleBookmarkMessage(self):
        if self.type[2] == "fetch":
            await self.__handleFetch()
        elif self.type[2] == "insert":
            await self.__handleInsert()
        elif self.type[2] == "remove":
            await self._handleRemove(peer="varchive")
        elif self.type[2] == "clear":
            await self._handleClear(peer="varchive")
        else:
            pass


class VarchiveBookmarkManager(BookmarkManager):
    def __init__(
        self,
        type: List[str],
        message: str,
        sendText: Callable,
        broadcastToIinas: Callable,
        broadcastToVarchives: Callable,
        putMessageToBroadcastVarchives: Callable,
        messageQueue: messageQueue.MessageQueue,
        ResourceMap: ResourceMapManager,
    ):
        super().__init__(
            type,
            message,
            sendText,
            broadcastToIinas,
            broadcastToVarchives,
            putMessageToBroadcastVarchives,
            messageQueue,
            ResourceMap,
        )

    async def __handleFetch(self):
        print(
            "BookmarkManager: received [Fetch] bookmarks requirement from [Varchive] for ",
            self.message["currentURL"],
        )
        bookmarkInfo = {
            "type": ["varchive", "bookmarks", "info"],
            "message": json.dumps(self.bookmarkJson),
        }
        await self.sendText(json.dumps(bookmarkInfo))

    async def __handleEditing(
        self,
    ):
        print(
            "BookmarkManager: received [Editing] bookmark requirement for ",
            self.message["currentURL"],
            "\ntimestamp:",
            self.message["timestamp"],
            "\nindex:",
            self.message["index"],
            "\ntitle:",
            self.message["title"],
            "\ndescription:",
            self.message["description"],
        )
        currentURL = self.message["currentURL"]
        index = self.message["index"]
        timestamp = self.message["timestamp"]
        bookmarks = self.bookmarkJson["bookmarks"]
        if index < len(bookmarks) and bookmarks[index]["timestamp"] == timestamp:
            bookmarks[index]["title"] = self.message["title"]
            bookmarks[index]["description"] = self.message["description"]
            self._syncBookmarksToFile()
        else:
            websocketMessage = {
                "type": ["varchive", "bookmarks", "editing-error"],
                "message": "Index [{}] is not consistent to timestamp [{}]. bookmarks had already changed before you submited".format(
                    index, timestamp
                ),
            }
            await self.sendText(json.dumps(websocketMessage))
            return

        # notify iina
        message = {
            "currentURL": currentURL,
            "timestamp": timestamp,
            "index": index,
            "title": self.message["title"],
            "description": self.message["description"],
        }
        bookmarkEditedInfo = {
            "type": ["iina", "bookmarks", "edited"],
            "message": json.dumps(message),
        }
        await self.broadcastToIinas(json.dumps(bookmarkEditedInfo))

        # notify varchive
        await self._sendMessageToVarchives("edited")

    async def handleBookmarkMessage(self):
        if self.type[2] == "fetch":
            await self.__handleFetch()
        elif self.type[2] == "editing":
            await self.__handleEditing()
        elif self.type[2] == "remove":
            await self._handleRemove(peer="iina")
        elif self.type[2] == "clear":
            await self._handleClear(peer="iina")
        else:
            pass
