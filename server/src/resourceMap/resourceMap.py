#!/usr/bin/env python3
# _*_coding:utf-8_*_

import json
import os
import datetime
import shutil
import urllib.parse
import re
from typing import *


class RecentManager:
    def __init__(
        self, recentPath: str, recentURL: str, SystemRunner, maxHistory: int = 100
    ):
        self.recentPath = recentPath
        self.SystemRunner = SystemRunner
        self.maxHistory = maxHistory
        self.recentURL = recentURL
        self.recentList = []
        self.metaMapRecentName = {}
        self.__initRecentList()

    def __getRecentPathByRecentName(self, recentName: str):
        return self.recentPath + "/" + recentName

    def __pop(self, index=0):
        recentName = self.recentList.pop(index)
        recentPath = self.__getRecentPathByRecentName(recentName)
        if not os.path.exists(recentPath):
            return
        linkInfo = ResourceMapManager.getLinkInfoBylinkPath(
            ResourceMapManager.getLinkPathByLinkDir(
                self.__getRecentPathByRecentName(recentName)
            )
        )
        metaFilename = linkInfo["metaLink"]
        self.metaMapRecentName.pop(metaFilename)
        # deleting local file is very dangerous
        shutil.rmtree(recentPath)

    def getRecentList(self):
        return [name for name in self.recentList]

    def openInVarchivebyMetaFilename(self, metaFilename: str):
        if metaFilename not in self.metaMapRecentName.keys():
            return
        recentName = self.metaMapRecentName[metaFilename]
        recentPath = self.__getRecentPathByRecentName(recentName)
        if not os.path.exists(recentPath):
            return
        recentURL = self.recentURL + "/" + recentName + "/details"
        self.SystemRunner.put(["open", recentURL])

    def __popByRecentName(self, recenName: str):
        # recentName may already be renamed by user
        if recenName in self.recentList:
            self.__pop(self.recentList.index(recenName))

    @staticmethod
    def matchTimeFormat(text: str):
        pattern = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.\d{3}")
        return pattern.match(text)

    def __initRecentList(self):
        for name in os.listdir(self.recentPath):
            if self.matchTimeFormat(name) and ResourceMapManager.isVarchiveLinkDir(
                self.__getRecentPathByRecentName(name)
            ):
                self.recentList.append(name)

        self.recentList.sort()
        for recentName in self.recentList:
            linkInfo = ResourceMapManager.getLinkInfoBylinkPath(
                ResourceMapManager.getLinkPathByLinkDir(
                    self.__getRecentPathByRecentName(recentName)
                )
            )
            self.metaMapRecentName[linkInfo["metaLink"]] = recentName
        while len(self.recentList) > self.maxHistory:
            self.__pop()

    def push(self, title: str, metaFilename: str):
        while len(self.recentList) >= self.maxHistory:
            self.__pop()
        currTime = datetime.datetime.now()
        formattedCurrTime = currTime.strftime("%Y-%m-%d_%H-%M-%S.%f")[:-3]
        recentName = formattedCurrTime + "-" + title
        if metaFilename in self.metaMapRecentName.keys():
            oldRecentName = self.metaMapRecentName[metaFilename]
            self.__popByRecentName(oldRecentName)
        self.metaMapRecentName[metaFilename] = recentName
        recentPath = self.__getRecentPathByRecentName(recentName)
        ResourceMapManager.createDirIfnotExists(recentPath)
        ResourceMapManager.createVarchiveLink(
            ResourceMapManager.getLinkPathByLinkDir(recentPath), metaFilename
        )
        self.recentList.append(recentName)


class ResourceMapManager:

    def __init__(
        self,
        Config: Dict,
        VARCHIVE_SUPPORT_PATH: str,
        USER_HOME_PATH: str,
        SERVER_SRC_ABS_PATH: str,
        FILE_MANAGER_ABS_PATH: str,
        SystemRunner,
    ):
        self.Config = Config
        self.SystemRunner = SystemRunner
        self.resourceMap = {}
        #  Store used details.json to avoid overwriting details.json while multiple running async infromation operations (eg. editing) are performing
        self.infoUsing = {}
        self.localFileHeader = "file://"
        self.postfixOfLink = ".varchive"
        self.relMetaPath = "meta/video"
        self.VARCHIVE_SUPPORT_PATH = VARCHIVE_SUPPORT_PATH
        self.USER_HOME_PATH = USER_HOME_PATH
        self.FILE_MANAGER_ABS_PATH = FILE_MANAGER_ABS_PATH
        self.metaPath = FILE_MANAGER_ABS_PATH + "/" + self.relMetaPath
        self.resourceMapPath = self.metaPath + "/resourceMap.json"
        self.macOSpath = FILE_MANAGER_ABS_PATH + "/video/macOS"
        self.AllPath = FILE_MANAGER_ABS_PATH + "/video/All"
        self.ArchivesPath = FILE_MANAGER_ABS_PATH + "/video/Archives"
        self.RecentPath = FILE_MANAGER_ABS_PATH + "/video/Recent"
        self.recentURL = "http://{}:{}/video/Recent".format(
            self.Config["varchive"]["host"], self.Config["varchive"]["port"]
        )
        ResourceMapManager.createDirIfnotExists(self.metaPath)
        ResourceMapManager.createDirIfnotExists(self.macOSpath)
        ResourceMapManager.symLinkIfnotExists(
            self.USER_HOME_PATH, f"{self.macOSpath}/Home"
        )
        ResourceMapManager.createDirIfnotExists(self.AllPath)
        ResourceMapManager.createDirIfnotExists(self.RecentPath)
        ResourceMapManager.createDirIfnotExists(self.ArchivesPath)
        self.recentManager = RecentManager(
            self.RecentPath, self.recentURL, SystemRunner, maxHistory=100
        )
        if os.path.exists(self.resourceMapPath):
            with open(self.resourceMapPath, mode="r", encoding="utf-8") as f:
                self.resourceMap = json.load(f)

    def __classifyFile(self, path: str, fileName: str) -> Dict:
        res = {"filename": fileName}
        if not os.path.isdir(path):
            res["type"] = "file"
        else:
            if self.isValidVarchiveVideo(path):
                res["type"] = "varchive-video"
            elif self.isVarchiveVideoLink(path):
                res["type"] = "invalid-varchive-video"
            else:
                res["type"] = "directory"
        return res

    def __createLinkDirToMetafile(self, linkPath: str, metaFilename: str):
        if not self.isValidVarchiveVideoLink(linkPath):
            ResourceMapManager.createDirIfnotExists(linkPath)
            ResourceMapManager.createVarchiveLink(
                self.getLinkPathByLinkDir(linkPath), metaFilename
            )

    def __handleListAll(self) -> List[Dict]:
        metaFilenames = os.listdir(self.metaPath)
        metaFilenames.sort(reverse=True)
        res = []
        for metaFilename in metaFilenames:
            if self.isValidMetaPath(self.metaPath + "/" + metaFilename):
                linkPath = self.AllPath + "/" + metaFilename
                self.__createLinkDirToMetafile(linkPath, metaFilename)
                res.append({"filename": metaFilename, "type": "varchive-video"})
        return (2, res)

    def __handleListRecent(self) -> List[Dict]:
        recentList = self.recentManager.getRecentList()
        recentList.sort(reverse=True)
        res = []
        for recent in recentList:
            if self.isValidVarchiveVideoLink(self.RecentPath + "/" + recent):
                res.append({"filename": recent, "type": "varchive-video"})
            else:
                res.append({"filename": recent, "type": "invalid-varchive-video"})
        return (2, res)

    def listDir(self, path: str) -> List[Dict]:
        realPath = self.FILE_MANAGER_ABS_PATH + "/" + path
        if realPath == self.AllPath:
            return self.__handleListAll()
        elif realPath == self.RecentPath:
            return self.__handleListRecent()
        else:
            if not os.path.exists(realPath):
                return (-1, [])
            if not os.path.isdir(realPath):
                return (1, [])
            if os.path.isdir(realPath) and self.isValidVarchiveVideo(realPath):
                return (0, [])
            res = []
            files = sorted(os.listdir(realPath))
            for file in files:
                res.append(self.__classifyFile(realPath + "/" + file, file))
            return (2, res)

    @staticmethod
    def createDirIfnotExists(path: str):
        if not os.path.exists(path):
            os.makedirs(path)

    @staticmethod
    def symLinkIfnotExists(src: str, dst: str):
        if not os.path.exists(dst):
            if os.path.exists(src):
                os.symlink(src, dst)

    def pushRecentByURL(self, url: str):
        metaFilename = self.getMetaFilenameByURL(url)
        if not metaFilename:
            return
        metaPath = self.getMetaPathByMetaFilename(metaFilename)
        if not os.path.exists(metaPath):
            return
        detailsPath = self.getDetailsPath(metaPath)
        details = {}
        with open(detailsPath, mode="r", encoding="utf-8") as f:
            details = json.load(f)
        self.recentManager.push(details["title"], metaFilename)

    def openInVarchivebyMetaFilename(self, metaFilename: str):
        self.recentManager.openInVarchivebyMetaFilename(metaFilename)

    def __syncToFile(self):
        with open(self.resourceMapPath, mode="w", encoding="utf-8") as f:
            f.write(json.dumps(self.resourceMap, ensure_ascii=False, indent=4))

    def getMetaRelPathByFilename(self, filename: str) -> str:
        return self.relMetaPath + "/" + filename

    def getMetaRelPathByLinkDir(self, linkDir: str) -> str:
        filename = self.getMetaFilenameByLink(linkDir)
        if not filename:
            return ""
        return self.getMetaRelPathByFilename(filename)

    def getMetaPathByMetaFilename(self, metaFilename: str) -> str:
        return self.metaPath + "/" + metaFilename

    def getMetaPathByLinkDir(self, linkDir: str) -> str:
        filename = self.getMetaFilenameByLink(linkDir)
        if not filename:
            return ""
        return self.getMetaPathByMetaFilename(filename)

    def getMetaFilenameByURL(self, url: str) -> str:
        (isNetworkResource, urlForEditing) = self.parseURL(url)
        if isNetworkResource:
            if not self.hasKey(urlForEditing):
                return ""
            else:
                return self.keyMapMetaFilename(urlForEditing)
        else:
            linkPath = self.getLinkDirByLocalPath(urlForEditing)
            return self.getMetaFilenameByLink(linkPath)

    def getMetaPathByURL(self, url: str) -> str:
        metaFilename = self.getMetaFilenameByURL(url)
        if not metaFilename:
            return ""
        return self.getMetaPathByMetaFilename(metaFilename)

    def getStatisticsPathByMetaPath(self, metaPath: str) -> str:
        return metaPath + "/" + "statistics.json"

    def getStatisticsPathByURL(self, url: str) -> str:
        metaPath = self.getMetaPathByURL(url)
        if not metaPath:
            return ""
        return self.getStatisticsPathByMetaPath(metaPath)

    @staticmethod
    def getLinkPathByLinkDir(linkDir: str):
        return linkDir + "/link-varchive.json"

    def isVarchiveVideoLink(self, path: str) -> bool:
        return os.path.isfile(self.getLinkPathByLinkDir(path))

    def isValidVarchiveVideoLink(self, path: str) -> bool:
        MetaPath = self.getMetaPathByLinkDir(path)
        if not MetaPath or not os.path.exists(MetaPath):
            return False
        return True

    def isValidMetaPath(self, path: str) -> bool:
        return os.path.realpath(
            os.path.dirname(path)
        ) == self.metaPath and os.path.exists(self.getDetailsPath(path))

    @staticmethod
    def isVarchiveLinkDir(path: str) -> bool:
        return os.path.isfile(path + "/link-varchive.json")

    def parseURL(self, url: str) -> List:
        headerLength = len(self.localFileHeader)
        if url[0:headerLength] == self.localFileHeader:
            urlForEditing = url[headerLength:]
            return (False, urlForEditing)
        else:
            return (True, url)

    def getLocalVideoPathByLinkDir(self, linkDir: str) -> str:
        if not linkDir.endswith(self.postfixOfLink):
            return ""
        return linkDir[0 : -len(self.postfixOfLink)]

    def addVideoPathIfAvailable(self, path: str):
        localVideoPath = self.getLocalVideoPathByLinkDir(path)
        if not os.path.exists(localVideoPath):
            return
        videoURL = self.localFileHeader + localVideoPath
        metaPath = self.getMetaPathByLinkDir(path)
        detailsPath = self.getDetailsPath(metaPath)
        details = {}
        with open(detailsPath, mode="r", encoding="utf-8") as f:
            details = json.load(f)
        path = details["path"]
        # firstUrl=path[0]
        if path[0]["url"] == videoURL:
            path[0]["isSelected"] = True
        else:
            indexes = [i for i in range(0, len(path)) if path[i]["url"] == videoURL]
            for i in reversed(indexes):
                path.pop(i)
            path.insert(0, {"url": videoURL, "isSelected": True})
        for url in path:
            if url["url"] in self.infoUsing:
                self.infoUsing[url["url"]]["path"] = path
        with open(detailsPath, mode="w", encoding="utf-8") as f:
            f.write(json.dumps(details, ensure_ascii=False, indent=4))

    def getLinkDirByLocalPath(self, localPath: str):
        dirname = os.path.dirname(localPath)
        fileName = os.path.basename(localPath)
        varchiveLinkDir = dirname + "/" + fileName + self.postfixOfLink
        return varchiveLinkDir

    def getLinkDirByVarchiveCurrentPath(self, varchiveCurrentPath: str):
        return self.FILE_MANAGER_ABS_PATH + varchiveCurrentPath

    def getStatisticPathByVarchiveCurrentPath(self, varchiveCurrentPath: str):
        linkPath = self.getLinkDirByVarchiveCurrentPath(varchiveCurrentPath)
        return self.getStatisticsPathByMetaPath(self.getMetaPathByLinkDir(linkPath))

    def getMetaFilenameByVarchiveCurrentPath(self, varchiveCurrentPath: str):
        linkDir = self.getLinkDirByVarchiveCurrentPath(varchiveCurrentPath)
        return self.getMetaFilenameByLink(linkDir)

    def getMetaPathByVarchiveCurrentPath(self, varchiveCurrentPath: str):
        metaFilename = self.getMetaFilenameByVarchiveCurrentPath(varchiveCurrentPath)
        return self.getMetaPathByMetaFilename(metaFilename)

    def deleteLinkDir(self, linkDir: str):
        if not self.isVarchiveVideoLink(linkDir):
            return
        else:
            # deleting local file is very dangerous
            shutil.rmtree(linkDir)

    def deleteURLFromVarchive(self, url: str):
        (isNetworkResource, urlForEditing) = self.parseURL(url)
        if isNetworkResource:
            self.delete(url)
        else:
            linkDir = self.getLinkDirByLocalPath(urlForEditing)
            self.deleteLinkDir(linkDir)

    def deleteVarchiveVideoByLinkDir(self, linkDir: str):
        metaPath = self.getMetaPathByLinkDir(linkDir)
        if not metaPath:
            return
        detailsPath = self.getDetailsPath(metaPath)
        details = {}
        with open(detailsPath, mode="r", encoding="utf-8") as f:
            details = json.load(f)
        path = details["path"]
        # urls = [url["url"] for url in path]
        for url in path:
            self.deleteURLFromVarchive(url["url"])
        shutil.rmtree(metaPath)
        if os.path.exists(linkDir):
            shutil.rmtree(linkDir)

    def hasVarchiveLink(self, localPath: str):
        varchiveLinkDir = self.getLinkDirByLocalPath(localPath)
        return self.isVarchiveVideoLink(varchiveLinkDir)

    def getDetailsPath(self, metaPath: str):
        return metaPath + "/details.json"

    def getBookmarkPath(self, metaPath: str):
        return metaPath + "/bookmark.json"

    def getWebpsPath(self, metaPath: str):
        return metaPath + "/webps"

    def isValidVarchiveVideo(self, path: str) -> bool:
        return self.isValidMetaPath(path) or self.isValidVarchiveVideoLink(path)

    def getMetaFilenameByLink(self, linkDir: str) -> str:
        if not self.isVarchiveVideoLink(linkDir):
            return ""
        linkPath = self.getLinkPathByLinkDir(linkDir)
        fJson = {}
        with open(linkPath, mode="r", encoding="utf-8") as f:
            fJson = json.load(f)
        return fJson["metaLink"]

    @staticmethod
    def createVarchiveLink(linkPath: str, metaFilename: str, **kwargs):
        with open(linkPath, mode="w", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {"metaLink": metaFilename, **kwargs}, ensure_ascii=False, indent=4
                )
            )

    @staticmethod
    def getLinkInfoBylinkPath(linkPath: str):
        fJson = {}
        with open(linkPath, mode="r", encoding="utf-8") as f:
            fJson = json.load(f)
        return fJson

    def createVarchiveLinkByMetaFilename(self, metaFilename: str, localPath: str):
        varchiveLinkDir = self.getLinkDirByLocalPath(localPath)
        ResourceMapManager.createDirIfnotExists(varchiveLinkDir)
        linkPath = self.getLinkPathByLinkDir(varchiveLinkDir)
        ResourceMapManager.createVarchiveLink(linkPath, metaFilename)

    def copyVarchiveLink(self, srcLinkPath: str, localPath: str):
        varchiveLinkDir = self.getLinkDirByLocalPath(localPath)
        ResourceMapManager.createDirIfnotExists(varchiveLinkDir)
        linkPath = self.getLinkPathByLinkDir(varchiveLinkDir)
        shutil.copyfile(srcLinkPath, linkPath)

    def createMetaPath(self, url: str, linkPath: str = "") -> str:
        currTime = datetime.datetime.now()
        formattedCurrTime = currTime.strftime("%Y-%m-%d_%H-%M-%S.%f")[:-3]
        newMetaPath = self.metaPath + "/" + formattedCurrTime
        archiveLinkPath = self.ArchivesPath + "/" + formattedCurrTime
        ResourceMapManager.createDirIfnotExists(newMetaPath)
        ResourceMapManager.createDirIfnotExists(self.getWebpsPath(newMetaPath))
        isNetworkResource = True
        if linkPath:
            isNetworkResource = False
            ResourceMapManager.createDirIfnotExists(linkPath)
            ResourceMapManager.createVarchiveLink(
                self.getLinkPathByLinkDir(linkPath), formattedCurrTime
            )
        self.__createLinkDirToMetafile(archiveLinkPath, formattedCurrTime)
        if isNetworkResource:
            self.insert(url, formattedCurrTime)
        return newMetaPath

    def unquoteURL(self, url: str) -> str:
        urlUnquoted = urllib.parse.unquote(url)
        while urlUnquoted != url:
            url = urlUnquoted
            urlUnquoted = urllib.parse.unquote(url)
        return url

    def hasKey(self, key: str) -> bool:
        key = self.unquoteURL(key)
        return key in self.resourceMap.keys()

    def keyMapPath(self, key: str) -> str:
        return self.metaPath + "/" + self.keyMapMetaFilename(key)

    def keyMapMetaFilename(self, key: str) -> str:
        key = self.unquoteURL(key)
        return self.resourceMap[key]

    def insert(self, url: str, path: str):
        url = self.unquoteURL(url)
        self.resourceMap[url] = path
        self.__syncToFile()

    def delete(self, url: str):
        url = self.unquoteURL(url)
        if not self.hasKey(url):
            return
        self.resourceMap.pop(url)
        self.__syncToFile()
