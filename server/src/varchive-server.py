#!/usr/bin/env python3
# _*_coding:utf-8_*_
from fastapi import (
    FastAPI,
    HTTPException,
    Path,
    Request,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import plistlib
import json
import os
from typing import *
import fileManager.fileManager as fileManager
import resourceMap.resourceMap as resourceMap
import subtitle.subtitile
import webSocketManager.webSocketManager as webSocketManager
import systemRun.systemRun as systemRun
from pathlib import Path
from pathvalidate import is_valid_filename, sanitize_filename
import asyncio

CURR_FILE_ABS_PATH = os.path.abspath(__file__)
SERVER_SRC_ABS_PATH = os.path.dirname(CURR_FILE_ABS_PATH)
CONFIG_FILE = SERVER_SRC_ABS_PATH + "/config.json"
FILE_MANAGER_ABS_PATH = os.path.abspath(SERVER_SRC_ABS_PATH + "/../fileManager")
SSL_KEY_FILE = os.path.abspath(SERVER_SRC_ABS_PATH + "/../pem/server.key")
SSL_CERT_FILE = os.path.abspath(SERVER_SRC_ABS_PATH + "/../pem/server.crt")
RESOURCE_MAP_FILE = SERVER_SRC_ABS_PATH + "/resourceMap.json"
USER_HOME_PATH = os.environ["HOME"]

Config = {}

with open(CONFIG_FILE, mode="r", encoding="utf-8") as f:
    Config = json.load(f)
HOST = Config["server"]["host"]
PORT = Config["server"]["port"]

SystemRunner = systemRun.SystemRun()
ResourceMap = resourceMap.ResourceMapManager(
    Config, SERVER_SRC_ABS_PATH, FILE_MANAGER_ABS_PATH, SystemRunner
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://{}:{}".format(Config["varchive"]["host"], Config["varchive"]["port"])
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Websocket
WEBSOCKET_MAX_CONNECTION = Config["server"]["maxWebsocketConnections"]
WebsocketIDCounter = 0
WebsocketManager = webSocketManager.WebSocketManager(
    Config, WEBSOCKET_MAX_CONNECTION, ResourceMap, SystemRunner
)

# Write varchive config for iina
iinaVarchiveDirURL = "{}/{}".format(USER_HOME_PATH, Config["iina"]["varchiveDirURL"])
ResourceMap.createDirIfnotExists(iinaVarchiveDirURL)
IinaVarchiveConfigPath = "{}/{}".format(
    iinaVarchiveDirURL, Config["iina"]["varchiveConfig"]
)
iinaVarchiveConfig = dict(
    websocket=dict(
        wssHost=HOST,
        wssPort=str(PORT),
        wssPath="/ws/iina/",
        maxConnections=WEBSOCKET_MAX_CONNECTION,
    ),
)
with open(IinaVarchiveConfigPath, "wb") as fp:
    plistlib.dump(iinaVarchiveConfig, fp)


class WebsockeID(BaseModel):
    id: int = -1


@app.get("/websocket/id", response_model=WebsockeID)
async def websocketID(request: Request, path: str = ""):
    ID = await WebsocketManager.getIDAvailableForVarchive()
    return WebsockeID(id=ID)


@app.websocket("/ws/iina/{clientID}")
async def websocketEndpointIINA(websocket: WebSocket, clientID: int):
    await WebsocketManager.connectIina(clientID, websocket)
    WebsocketManager.messagesFromIina[clientID].clear()
    try:
        tasks_list = [
            asyncio.create_task(
                WebsocketManager.sendMessageToIina(clientID, websocket)
            ),
            asyncio.create_task(
                WebsocketManager.receiveMessageFromIina(clientID, websocket)
            ),
        ]
        await asyncio.gather(*tasks_list)

    except WebSocketDisconnect:
        await WebsocketManager.sendDispairedInfoToVarchiveByIinaID(clientID)
        await WebsocketManager.disconnectIina(clientID)


@app.websocket("/ws/varchive/video/details/{clientID}")
async def websocketEndpointVarchive(websocket: WebSocket, clientID: int):
    await WebsocketManager.connectVarchive(clientID, websocket)
    WebsocketManager.messagesFromVarchiveVideo[clientID].clear()
    try:
        tasks_list = [
            asyncio.create_task(
                WebsocketManager.sendMessageToVarchiveVideoDetails(clientID, websocket)
            ),
            asyncio.create_task(
                WebsocketManager.receiveMessageFromVarchiveVideoDetails(
                    clientID, websocket
                )
            ),
        ]
        await asyncio.gather(*tasks_list)
    except WebSocketDisconnect:
        WebsocketManager.disconnectVarchive(clientID)


# filemanager
FileManager = fileManager.FileManager(FILE_MANAGER_ABS_PATH, ResourceMap)


class ListFiles(BaseModel):
    fileStatusCode: int = -1
    fileList: List[Dict] = []


@app.get("/filemanager", response_model=ListFiles)
async def videoListDir(request: Request, path: str = ""):
    res = FileManager.listDir(path)
    return ListFiles(fileStatusCode=res[0], fileList=res[1])


class RealDetailsPath(BaseModel):
    videoPath: str = ""


@app.get("/filemanager/realpath", response_model=RealDetailsPath)
async def getRealVideoPath(request: Request, path: str = ""):
    realPath = FILE_MANAGER_ABS_PATH + path
    if ResourceMap.isVarchiveVideoLink(realPath):
        ResourceMap.addVideoPathIfAvailable(realPath)
        path = "/" + ResourceMap.getMetaRelPathByLinkDir(realPath)
    return RealDetailsPath(videoPath=path)


class VarchiveLinkDir(BaseModel):
    linkDir: str = ""


@app.post("/filemanager/varchive/delete/")
async def deleteVarchiveVideo(request: Request, vld: VarchiveLinkDir):
    realPath = FILE_MANAGER_ABS_PATH + vld.linkDir
    if not ResourceMap.isVarchiveVideoLink(realPath):
        raise HTTPException(status_code=400, detail="Not a varhive link dir.")
    ResourceMap.deleteVarchiveVideoByLinkDir(linkDir=realPath)
    return {"msg": "deleted!"}


class RenameVarchiveLinkDir(BaseModel):
    srcLinkDir: str = ""
    dstLinkName: str = ""


@app.post("/filemanager/varchive/rename/")
async def renameVarchiveLinkDir(request: Request, rvld: RenameVarchiveLinkDir):
    realPath = FILE_MANAGER_ABS_PATH + rvld.srcLinkDir
    if not ResourceMap.isVarchiveVideoLink(realPath):
        raise HTTPException(status_code=400, detail="Not a varhive link dir.")
    dirname = os.path.dirname(realPath)
    if not is_valid_filename(rvld.dstLinkName):
        rvld.dstLinkName = sanitize_filename(rvld.dstLinkName)
    newLinkDir = dirname + "/" + rvld.dstLinkName
    if os.path.exists(newLinkDir):
        raise HTTPException(
            status_code=400, detail=rvld.dstLinkName + " already exists!"
        )
    os.rename(realPath, newLinkDir)
    return {"msg": "renamed!"}


@app.get("/filemanager/download")
async def download(path: str):
    path = FILE_MANAGER_ABS_PATH + path
    if not os.path.isfile(path):
        raise HTTPException(status_code=400, detail="Not a file or does not exist")

    fr = FileResponse(
        path=path,
        filename=Path(path).name,
    )
    return fr


class FetchJson(BaseModel):
    jsonStr: str = ""


@app.get("/filemanager/json", response_model=FetchJson)
async def fetchJson(request: Request, path: str = ""):
    path = FILE_MANAGER_ABS_PATH + path
    if not os.path.isfile(path):
        raise HTTPException(status_code=400, detail="Not a file or does not exist")
    fJson = {}
    with open(path, mode="r", encoding="utf-8") as f:
        fJson = json.load(f)
    return FetchJson(jsonStr=json.dumps(fJson))


@app.get("/filemanager/open", response_model=FetchJson)
async def openFileOnFinder(request: Request, path: str = ""):
    path = FILE_MANAGER_ABS_PATH + "/" + path
    if not os.path.exists(path):
        raise HTTPException(status_code=400, detail="Not a file or does not exist")
    command = ["open", path]
    SystemRunner.put(command)
    return {"statue": "running"}


# subtitle
class SubTitleParsed(BaseModel):
    subParseCode: int = -1
    subParsedJsonStr: str = ""


@app.get("/subtitle/parser", response_model=SubTitleParsed)
async def parseSubtitle(request: Request, path: str = ""):
    try:
        resParsed = subtitle.subtitile.Subtitle(path).readAndParse()
        return SubTitleParsed(subParseCode=0, subParsedJsonStr=json.dumps(resParsed))
    except Exception as e:
        print(f"{e}")
        return SubTitleParsed(subParseCode=-1, subParsedJsonStr=e)


if __name__ == "__main__":
    uvicorn.run(
        app="varchive-server:app",
        host=HOST,
        port=PORT,
        reload=False,
        ssl_keyfile=SSL_KEY_FILE,
        ssl_certfile=SSL_CERT_FILE,
    )
