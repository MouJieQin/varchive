import os
import json
from typing import *
import resourceMap.resourceMap as resourceMap


class FileManager:
    def __init__(self, root: str, ResourceMap: resourceMap.ResourceMapManager):
        self.root = root
        self.ResourceMap = ResourceMap

    def __classifyFile(self, path: str, fileName: str) -> Dict:
        res = {"filename": fileName}
        if not os.path.isdir(path):
            res["type"] = "file"
        else:
            if self.ResourceMap.isVarchiveVideo(path):
                if self.ResourceMap.isValidVarchiveVideoLink(path):
                    res["type"] = "varchive-video"
                else:
                    res["type"] = "invalid-varchive-video"
            else:
                res["type"] = "directory"
        return res

    def listDir(self, path: str) -> List[Dict]:
        realPath = self.root + "/" + path
        if not os.path.exists(realPath):
            return (-1, [])
        if not os.path.isdir(realPath):
            return (1, [])
        if os.path.isdir(realPath) and self.ResourceMap.isValidVarchiveVideoLink(realPath):
            return (0, [])
        res = []
        files = sorted(os.listdir(realPath))
        for file in files:
            res.append(self.__classifyFile(realPath + "/" + file, file))
        return (2, res)
