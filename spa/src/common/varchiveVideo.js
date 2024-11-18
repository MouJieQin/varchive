import config from "@/config.json";
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
