import config from "@/config.json";
import { ElMessage, ElNotification, ElMessageBox } from "element-plus";

export const serverOperate = async (command) => {
    const url = config.server.concat(config.post.varchiveServer);
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                command: command,
            }),
        });
        if (response.ok) {
            return { returnCode: 0, json: await response.json() };
        } else {
            const message = await response.json();
            ElMessageBox.alert(message.detail, "Error", {
                confirmButtonText: "OK",
                type: "error",
            });
            return { returnCode: 1 };
        }
    } catch (error) {
        console.log("Request Failed:", error);
        return { returnCode: 1 };
    }
};

export const fileOperate = async (path, command) => {
    const url = config.server.concat(config.post.fileOperation);
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                path: path,
                command: command,
            }),
        });
        if (!response.ok) {
            const message = await response.json();
            ElMessage({
                message: message.detail,
                type: "error",
            });
            return { returnCode: 1 };
        }
        ElMessage({
            message: command + "!",
            type: "success",
        });
        return { returnCode: 0 };
    } catch (error) {
        console.log("Request Failed:", error);
        return { returnCode: 1 };
    }
};

export const loadVideoInfo = async (path) => {
    const splits = path.split("/");
    const currentPath = splits.slice(0, splits.length - 1).join("/");
    const url_ = config.server.concat(
        config.get.realpath,
        "?path=",
        currentPath
    );
    var videoPath = "";
    try {
        const response = await fetch(url_);
        if (!response.ok) {
            throw new Error(await response.text());
        }
        const resJson = await response.json();
        videoPath = resJson.videoPath;
        if (videoPath === "") {
            return {
                returnCode: 1,
            };
        }
    } catch (error) {
        console.log("Request Failed:", error);
        return {
            returnCode: 1,
        };
    }
    const webpPath = config.server.concat(
        config.get.fileDownload,
        "?path=",
        videoPath
    );
    const url = config.server.concat(
        config.get.fetchJson,
        "?path=",
        videoPath,
        "/details.json"
    );
    console.log(url);
    var videoInfo = {};
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(await response.text());
        }
        const resJson = await response.json();
        videoInfo = JSON.parse(resJson.jsonStr);
    } catch (error) {
        console.log("Request Failed:", error);
        return {
            returnCode: 1,
        };
    }
    return {
        returnCode: 0,
        currentPath: currentPath,
        videoPath: videoPath,
        webpPath: webpPath,
        videoInfo: videoInfo,
    };
};

export const loadBookmarks = async (videoPath) => {
    const url = config.server.concat(
        config.get.fetchJson,
        "?path=",
        videoPath,
        "/bookmark.json"
    );
    console.log(url);
    var bookmarks = {};
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(await response.text());
        }
        const resJson = await response.json();
        bookmarks = JSON.parse(resJson.jsonStr);
    } catch (error) {
        console.log("Request Failed:", error);
        return {
            returnCode: 1,
        };
    }
    return {
        returnCode: 0,
        bookmarks: bookmarks,
    };
};
