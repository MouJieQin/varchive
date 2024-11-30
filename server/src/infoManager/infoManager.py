#! /usr/bin/env python3.9
# _*_coding:utf-8_*_

from bookmarkManager.bookmarkManager import *
from videoStatistics.videoStatistics import *


class IINAinfoManager(IINAbookmarkManager):
    def __init__(
        self,
        type: List[str],
        message: str,
        sendText: Callable,
        broadcastToIinas: Callable,
        broadcastToVarchives: Callable,
        putMessageToBroadcastVarchives: Callable,
        wsApp: Callable,
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
        self.wsApp = wsApp
        self.previewWebpOutputPaths = []
        self.__initData()

    def __initData(self):
        if os.path.exists(self.detailsPath):
            if self.detailsPath in self.ResourceMap.infoUsing.keys():
                self.infoJson = self.ResourceMap.infoUsing[self.detailsPath]
            else:
                with open(self.detailsPath, mode="r", encoding="utf-8") as f:
                    self.ResourceMap.infoUsing[self.detailsPath] = json.load(f)
                self.infoJson = self.ResourceMap.infoUsing[self.detailsPath]

    async def __initDetails(self):
        if os.path.exists(self.detailsPath):
            message = self.genNotificationMessageForIina(
                "notification",
                self.url,
                "Already Archived",
                "{} has been archived previously! A new cover will be generated.".format(
                    self.url
                ),
                3,
            )
            await self.sendText(message)
            return
        self._initDetails()
        message = self.genNotificationMessageForIina(
            "success",
            self.url,
            "Archived",
            "{} is archived!".format(self.url),
            3,
        )
        await self.sendText(message)
        self.ResourceMap.infoUsing[self.detailsPath] = self.infoJson

    def __putDetailsMessageForVarchive(self):
        detailsInfo = {
            "type": ["varchive", "details", "info", "update"],
            "message": json.dumps(self.infoJson),
        }
        self.messageQueue.put(json.dumps(detailsInfo))

    async def __genCover(self) -> int:
        startTime = float(self.type[2])
        videoEditor = videoEditing.VideoEditing(
            self.urlForEditing, self.isNetworkResource
        )
        if self.isNetworkResource:
            # Send notification to varchive due to a long time when acquiring network video resource duration.
            message = self.genNotificationMessageForVarchive(
                "notification",
                "notification",
                "Acquiring network video resource duration, please wait.",
                f"{startTime}s {self.url}",
            )
            self.putMessageToBroadcastVarchives(message)
        videoDuration = videoEditor.getVideoDuration()
        if videoDuration <= 0:
            message = self.genNotificationMessageForVarchive(
                "notification", "error", "Cannot acquire the video duration.", self.url
            )
            self.putMessageToBroadcastVarchives(message)
            return -1
        if videoDuration <= self.duration:
            message = self.genNotificationMessageForVarchive(
                "notification",
                "error",
                "The video duration is too short to generate cover.",
                "[{}s]: {}".format(videoDuration, self.url),
            )
            self.putMessageToBroadcastVarchives(message)
            return -1
        if startTime + self.duration > videoDuration:
            startTime = videoDuration - self.duration
        endTime = startTime + self.duration
        self.infoJson["cover"] = {
            "webp": "/icons/landscape.png",
            "cover": "/icons/landscape.png",
            "startTime": startTime,
            "endTime": endTime,
        }
        cover = self.infoJson["cover"]
        coverPath = self.webpsDir + "/0" + videoEditing.VideoEditing.webpFormat
        videoEditor.genWebp(
            startTime,
            endTime,
            coverPath,
            self._genWebpCallback,
            outPath=coverPath,
            clip=cover,
            VEditor=videoEditor,
            syncVarchive=self._syncInformation,
            isPreview=False,
            previewWebpOutputPaths="",
            previewWebpCoverPath="",
            cover=cover,
        )

    def __handleGenCover(self):
        self.threadAsync.addAsyncFunction(self.__genCover)

    async def __handleInfoWithoutPreview(self):
        await self.__initDetails()
        await self.__handleOpenInVarchive()
        self.__handleGenCover()
        self.__putDetailsMessageForVarchive()

    async def __handleOpenInVarchive(self):
        currentURL = self.message["currentURL"]
        metaFilename = self.ResourceMap.getMetaFilenameByURL(currentURL)
        if not metaFilename:
            message = self.genNotificationMessageForIina(
                "error", currentURL, "Not Varchived yet.", currentURL, 3
            )
            await self.sendText(message)
            return
        allURL = self.ResourceMap.getAllURLbyMetaFilename(metaFilename)
        if not self.wsApp()["status"]:
            self.ResourceMap.SystemRunner.put(["open", allURL])
        else:
            self.wsApp()["sendTextToApp"](
                json.dumps(
                    {
                        "type": [
                            "app",
                            "newWindow",
                            allURL,
                        ]
                    }
                )
            )

    async def handleMessage(self):
        if self.type[1] == "bookmarks":
            await self.handleBookmarkMessage()
        elif self.type[1] == "archive":
            await self.__handleInfoWithoutPreview()
        elif self.type[1] == "openInVarchive":
            await self.__handleOpenInVarchive()
        else:
            pass


class VarchiveInfoManager(VarchiveBookmarkManager):
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
        self.previewWebpOutputPaths = []
        self.__initData()

    def __initData(self):
        if os.path.exists(self.detailsPath):
            if self.detailsPath in self.ResourceMap.infoUsing.keys():
                self.infoJson = self.ResourceMap.infoUsing[self.detailsPath]
            else:
                with open(self.detailsPath, mode="r", encoding="utf-8") as f:
                    self.ResourceMap.infoUsing[self.detailsPath] = json.load(f)
                self.infoJson = self.ResourceMap.infoUsing[self.detailsPath]

    async def __sendEditingErrorToVarchive(self, errorMessage: str):
        await self._sendDetailsMessageForVarchive(
            "editing-error", isBroadcast=False, message=errorMessage
        )

    async def __syncEditedInformation(self):
        self._syncInfoToFile()
        await self._sendDetailsMessageForVarchive("edited", isBroadcast=True)

    async def __syncPreviewDeletedInformation(self):
        self._syncInfoToFile()
        await self._sendDetailsMessageForVarchive("preview-cleared", isBroadcast=True)

    async def __handleInsertURLs(
        self,
        metaFilename: str,
        linkPath: str,
        newURLsNotInOld: List[str],
        isOnlyForCheck: bool = True,
    ) -> bool:
        for url in newURLsNotInOld:
            (isNetworkResource, urlForEditing) = self.ResourceMap.parseURL(url)
            if isNetworkResource:
                if self.ResourceMap.hasKey(urlForEditing):
                    await self.__sendEditingErrorToVarchive(
                        "{} already has been linked to the meta file {}!".format(
                            urlForEditing,
                            self.ResourceMap.keyMapPath(urlForEditing),
                        )
                    )
                    return False
                if not isOnlyForCheck:
                    self.ResourceMap.insert(urlForEditing, metaFilename)
            else:
                if not os.path.exists(urlForEditing):
                    await self.__sendEditingErrorToVarchive(url + " does not exist!")
                    return False
                if self.ResourceMap.hasVarchiveLink(urlForEditing):
                    await self.__sendEditingErrorToVarchive(
                        url + " already has a varchive link file!"
                    )
                    return False
                if not isOnlyForCheck:
                    if self.isNetworkResource:
                        self.ResourceMap.createVarchiveLinkByMetaFilename(
                            metaFilename, urlForEditing
                        )
                    else:
                        self.ResourceMap.copyVarchiveLink(linkPath, urlForEditing)
        return True

    async def __handleEditingForPath(
        self,
        urls: List[Dict],
    ):
        if len(urls) == 0:
            await self.__sendEditingErrorToVarchive(
                "At least one URL have to be left to link to the meta data!"
            )
            return
        for path in urls:
            path["url"] = path["url"].strip()
        oldURLs = [path["url"] for path in self.infoJson["path"]]
        newURLs = [path["url"] for path in urls]
        oldURLsNotInNew = [url for url in oldURLs if url not in newURLs]
        newURLsNotInOld = [url for url in newURLs if url not in oldURLs]
        if self.isNetworkResource:
            metaFilename = self.ResourceMap.keyMapMetaFilename(self.url)
            if not await self.__handleInsertURLs(
                metaFilename, "", newURLsNotInOld, isOnlyForCheck=True
            ):
                return
            await self.__handleInsertURLs(
                metaFilename, "", newURLsNotInOld, isOnlyForCheck=False
            )
        else:
            linkPath = self.ResourceMap.getLinkPathByLinkDir(self.varchiveLinkDir)
            if not os.path.exists(linkPath):
                await self.__sendEditingErrorToVarchive(linkPath + " does not exist!")
                return
            metaFilename = self.ResourceMap.getMetaFilenameByLink(self.varchiveLinkDir)
            if not metaFilename:
                await self.__sendEditingErrorToVarchive(
                    "Cannot acquire meta path from " + linkPath
                )
                return
            if not await self.__handleInsertURLs(
                metaFilename, linkPath, newURLsNotInOld, isOnlyForCheck=True
            ):
                return
            await self.__handleInsertURLs(
                metaFilename, linkPath, newURLsNotInOld, isOnlyForCheck=False
            )
        for url in oldURLsNotInNew:
            self.ResourceMap.deleteURLFromVarchive(url)

        self.infoJson["path"] = urls
        await self.__syncEditedInformation()

    async def __handleEditing(self):
        newInfo = self.message
        print("newInfo:", newInfo)
        for key, value in newInfo.items():
            if key == "title":
                self.infoJson[key] = value
            elif key == "description":
                self.infoJson[key] = value
            elif key == "info":
                self.infoJson[key] = value
            elif key == "path":
                await self.__handleEditingForPath(value)
                return
            else:
                pass
        await self.__syncEditedInformation()

    async def __genPreview(self) -> int:
        if self.isNetworkResource:
            # Send notification to varchive due to a long time when acquiring network video resource duration.
            message = self.genNotificationMessageForVarchive(
                "notification",
                "notification",
                "Acquiring network video resource duration, please wait.",
                self.url,
            )
            await self.sendText(message)
        videoEditor = videoEditing.VideoEditing(
            self.urlForEditing, self.isNetworkResource
        )
        videoDuration = videoEditor.getVideoDuration()
        if videoDuration <= 0:
            message = self.genNotificationMessageForVarchive(
                "notification", "error", "Cannot acquire the video duration.", self.url
            )
            await self.sendText(message)
            return -1
        # percentages = [i / 100 for i in range(5, 100, 20)]
        percentages = [i / 100 for i in range(5, 100, 10)]
        if percentages[-1] * videoDuration + self.duration > videoDuration:
            message = self.genNotificationMessageForVarchive(
                "notification",
                "error",
                "The video duration is too short to generate previews.",
                "[{}s]: {}".format(videoDuration, self.url),
            )
            await self.sendText(message)
            return -1
        self._createWebpDirIfNotExist()
        timestamps = [percentage * videoDuration for percentage in percentages]
        previewWebpOutputPaths = []
        previewWebpCoverPath = (
            self.webpsDir + "/0" + videoEditing.VideoEditing.webpFormat
        )
        cover = self.infoJson["cover"]
        for timestamp in timestamps:
            startTime = timestamp
            endTime = startTime + self.duration
            outputPath = videoEditor.getWebpPath(self.webpsDir, startTime, endTime)
            self.infoJson["previews"]["clips"].append(
                {
                    "webp": "/icons/landscape.png",
                    "cover": "/icons/landscape.png",
                    "startTime": startTime,
                    "endTime": endTime,
                }
            )
            self._syncInformation()
            clip = self.infoJson["previews"]["clips"][-1]
            videoEditor.genWebp(
                startTime,
                endTime,
                outputPath,
                self._genWebpCallback,
                outPath=outputPath,
                clip=clip,
                VEditor=videoEditor,
                syncVarchive=self._syncInformation,
                isPreview=True,
                previewWebpOutputPaths=previewWebpOutputPaths,
                previewWebpCoverPath=previewWebpCoverPath,
                cover=cover,
            )

    def __handleGenPreview(self):
        self.threadAsync.addAsyncFunction(self.__genPreview)

    async def __handleClearPreview(self):
        clips = self.infoJson["previews"]["clips"]
        for clip in clips:
            self._cancelClip(clip)
            self._removeClipFiles(clip)
        self.infoJson["previews"]["clips"] = []
        await self.__syncPreviewDeletedInformation()

    async def __handleStatisticMessage(self):
        statisticPath = self.ResourceMap.getStatisticPathByVarchiveCurrentPath(
            self.message["varchiveCurrentPath"]
        )
        if self.type[2] == "fetch":
            print(
                "VarchiveInfoManager: received [Fetch] statistic requirement for ",
                self.message["varchiveCurrentPath"],
            )
            vs = VideoStatistics()
            if os.path.exists(statisticPath):
                vs.load(statisticPath)
            statistics = vs.getStatistics()
            statisticsInfo = {
                "type": ["varchive", "statistics", "info"],
                "message": json.dumps(statistics),
            }
            await self.sendText(json.dumps(statisticsInfo))
        else:
            pass

    async def handleMessage(
        self,
    ):
        if self.type[1] == "bookmarks":
            await self.handleBookmarkMessage()
        elif self.type[1] == "statistics":
            await self.__handleStatisticMessage()
        elif self.type[1] == "info-editing":
            await self.__handleEditing()
        elif self.type[1] == "generate-preview":
            self.__handleGenPreview()
        elif self.type[1] == "clear-preview":
            await self.__handleClearPreview()
        else:
            pass
