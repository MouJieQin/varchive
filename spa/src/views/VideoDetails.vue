<template>
    <div v-if="isPluginEnvironment">
        <el-tabs v-model="tabLabelShowing" type="border-card">
            <div style="float: right; text-align: right;">
                <el-button-group class="ml-4">
                    <el-button v-if="connection === 'serverConnected'" :icon="ConnectionRaw" type="primary" plain
                        circle>
                    </el-button>
                    <el-button v-else-if="connection === 'iinaConnected'" :icon="ConnectionRaw" type="success" circle>
                    </el-button>
                    <el-button v-else :icon="ConnectionRaw" type="warning" circle>
                    </el-button>
                    <el-button :icon="DeleteRaw" type="danger" plain circle style="float:right" @click="deleteVarchive">
                    </el-button>
                </el-button-group>
            </div>
            <el-tab-pane label="Introduction" name="Introduction">
                <Introduction :isPluginEnvironment="isPluginEnvironment" :changeInfo="changeInfo" :renameOption="renameOption" :openInIINA="openInIINA"
                    :getRealImagSrc="getRealImagSrc" :setSeletedURL="(url) => { urlSelected = url }"
                    :updateURL="updateURL" :renameVarchiveLinkDir="renameVarchiveLinkDir" :infoEditing="infoEditing"
                    :videoInfo="videoInfo" :urlSelected="urlSelected" />
            </el-tab-pane>
            <el-tab-pane label="Preview" name="Preview">
                <Preview :webpPath="webpPath" :videoInfo="videoInfo" :getMessageToServer="getMessageToServer"
                    :sendMessage="sendMessage" :seekTo="seekTo" />
            </el-tab-pane>
            <el-tab-pane label="Bookmark" name="Bookmark">
                <Bookmarks :setIsBookmarksMouseOver="(val) => { isBookmarksMouseOver = val }"
                    :isPluginEnvironment="isPluginEnvironment" :clearBookmarks="clearBookmarks"
                    :bookmarkInfo="bookmarkInfo" :seekTo="seekTo" :removeBookmark="removeBookmark"
                    :highlightTextWithMatch="highlightTextWithMatch" :editBookmark="editBookmark"
                    :webpPath="webpPath" />
            </el-tab-pane>
            <el-tab-pane label="Subtitle" name="Subtitle">
                <Subtitles :isPluginEnvironment="isPluginEnvironment" :subPageInfo="subPageInfo" :playerMessage="playerMessage" :subtitleInfoes="subtitleInfoes"
                    :subShowing="subShowing" :setSubtitleInfoes="setSubtitleInfoes" :setSubShowing="setSubShowing"
                    :highlightTextWithMatch="highlightTextWithMatch" :seekTo="seekTo" />
            </el-tab-pane>
            <el-tab-pane label="Statistics" name="Statistics">
                <Statistics  :isPluginEnvironment="isPluginEnvironment" :statistics="statistics" :seekTo="seekTo" />
            </el-tab-pane>
        </el-tabs>
    </div>
    <div v-else>
        <Anchor class="sticky" />
        <div id="video-details">
            <div style="float: right; text-align: right;">
                <el-button-group class="ml-4">
                    <el-button v-if="connection === 'serverConnected'" :icon="ConnectionRaw" type="primary" plain
                        circle>
                    </el-button>
                    <el-button v-else-if="connection === 'iinaConnected'" :icon="ConnectionRaw" type="success" circle>
                    </el-button>
                    <el-button v-else :icon="ConnectionRaw" type="warning" circle>
                    </el-button>
                    <el-button :icon="DeleteRaw" type="danger" plain circle style="float:right" @click="deleteVarchive">
                    </el-button>
                </el-button-group>
            </div>
            <div class="container">
                <Introduction :changeInfo="changeInfo" :renameOption="renameOption" :openInIINA="openInIINA"
                    :getRealImagSrc="getRealImagSrc" :setSeletedURL="(url) => { urlSelected = url }"
                    :updateURL="updateURL" :renameVarchiveLinkDir="renameVarchiveLinkDir" :infoEditing="infoEditing"
                    :videoInfo="videoInfo" :urlSelected="urlSelected" />
                <Preview :webpPath="webpPath" :videoInfo="videoInfo" :getMessageToServer="getMessageToServer"
                    :sendMessage="sendMessage" :seekTo="seekTo" />
                <br style="clear:both" />
                <Bookmarks :setIsBookmarksMouseOver="(val) => { isBookmarksMouseOver = val }"
                    :clearBookmarks="clearBookmarks" :bookmarkInfo="bookmarkInfo" :seekTo="seekTo"
                    :removeBookmark="removeBookmark" :highlightTextWithMatch="highlightTextWithMatch"
                    :editBookmark="editBookmark" :webpPath="webpPath" />
                <br style="clear:both" />
                <Subtitles :subPageInfo="subPageInfo" :playerMessage="playerMessage" :subtitleInfoes="subtitleInfoes"
                    :subShowing="subShowing" :setSubtitleInfoes="setSubtitleInfoes" :setSubShowing="setSubShowing"
                    :highlightTextWithMatch="highlightTextWithMatch" :seekTo="seekTo" />
                <br style="clear:both" />
                <Statistics :statistics="statistics" :seekTo="seekTo" />
            </div>
        </div>
        <el-backtop :bottom="20" />
    </div>
</template>

<script>
import config from '@/config.json'
import { Connection, Search, View, Hide, CircleCheck, CircleCheckFilled, Warning, WarningFilled, Check, Close, Edit, Refresh, Delete, VideoPlay, VideoPause, Film, RefreshLeft, Grid, List } from '@element-plus/icons-vue'
import WebpPreview from '@/components/WebpPreview.vue'
import Bookmark from '@/components/Bookmark.vue'
import Subtitle from '@/components/Subtitle.vue'
import SubtitleSelector from '@/components/SubtitleSelector.vue'
import VideoURL from '@/components/VideoURL.vue'
import Introduction from '@/views/Introduction.vue'
import Preview from '@/views/Preview.vue'
import Bookmarks from '@/views/Bookmarks.vue'
import Subtitles from '@/views/Subtitles.vue'
import Anchor from '@/views/Anchor.vue'
import Statistics from '@/views/Statistics.vue'
import { loadVideoInfo } from '@/common/varchiveVideo.js'
import { ElMessage, ElNotification, ElMessageBox } from 'element-plus';
import { markRaw } from 'vue'

export default {
    data() {
        return {
            WarningFilledRaw: markRaw(WarningFilled),
            DeleteRaw: markRaw(Delete),
            CircleCheckFilledRaw: markRaw(CircleCheckFilled),
            CircleCheckRaw: markRaw(CircleCheck),
            WarningFilledRaw: markRaw(WarningFilled),
            WarningRaw: markRaw(Warning),
            EditRaw: markRaw(Edit),
            CloseRaw: markRaw(Close),
            CheckRaw: markRaw(Check),
            ConnectionRaw: markRaw(Connection),
            VideoPlayRaw: markRaw(VideoPlay),
            VideoPauseRaw: markRaw(VideoPause),
            FilmRaw: markRaw(Film),
            GridRaw: markRaw(Grid),
            ListRaw: markRaw(List),
            RefreshLeftRaw: markRaw(RefreshLeft),
            tabLabelShowing: "Bookmark",
            isPluginEnvironment: false,
            currentPath: "",
            connection: "closed",
            isInfoEditing: false,
            infoEditing: {},
            videoInfo: {},
            urlSelected: "",
            videoPath: "",
            webpPath: "",
            isCoverMouseOver: false,
            isPlayPreview: false,
            isPlayBookmarks: false,
            isWebpsOnly: false,
            bookmarkPattern: "",
            webSocket: {},
            isBeforeUnmount: false,
            playerMessage: {},
            iinaCommand: "",
            hasNewIinaCommamd: false,
            subtitleInfoes: [],
            videoPos: 0.0,
            index: 1,
            subtitlePlayingID: "",
            bookmarkPlayingID: "",
            subShowing: "",
            isBookmarksMouseOver: false,
            bookmarkInfo: {},
            isHidePreview: false,
            isMouseOverPreview: false,
            isHideBookmarks: false,
            isMouseoverBookmarks: false,
            isHideSubtitles: false,
            isMouseoverSubtitles: false,
            subPageInfo: {
                isSubtitleMouseOver: false,
                isStopAutoScrollSub: false,
                subPattern: "",
            },
            isHideStatistics: false,
            isMouseoverStatistics: false,
            statistics: {},
        }
    },

    components: { Anchor, Introduction, Preview, Bookmarks, Subtitles, Statistics, Search, Refresh, CircleCheck, CircleCheckFilled, WarningFilled, Edit, Delete, RefreshLeft, Check, Close, View, Hide, VideoPlay, VideoPause, Film, Grid, List, WebpPreview, Bookmark, Subtitle, SubtitleSelector, VideoURL },

    watch: {
        videoPos(newVideoPos, oldVideoPos) {
            // Automatically scrolling subtitle with pos
            if (this.subtitleInfoes.length !== 0) {
                const index = this.binarySearch(this.subtitleInfoes, 0, this.subtitleInfoes.length, newVideoPos, ((val, subtitleInfo) => {
                    return val < subtitleInfo.startTime
                }))
                if (index !== 0) {
                    this.gotoSubPageByID("subtitle-scroll-container", this.subShowing.concat('-', this.subtitleInfoes[index - 1].startTimeFormat))
                }
                this.index = index - 1
            }

            // Automatically scrolling bookmark with pos
            if (this.bookmarkInfo.bookmarks.length !== 0) {
                const bIndex = this.binarySearch(this.bookmarkInfo.bookmarks, 0, this.bookmarkInfo.bookmarks.length, newVideoPos, ((val, bookmark) => {
                    return val < bookmark.timestamp
                }))
                if (bIndex !== 0) {
                    this.gotoBookmarkPageByID("bookmarks-scroll-container", "bookmark-".concat(this.bookmarkInfo.bookmarks[bIndex - 1].timestamp.toString()))
                }
            }

        },
        subtitlePlayingID(newID, oldID) {
            if (oldID !== "") {
                var ele = document.getElementById(oldID)
                if (typeof ele != 'null') {
                    try {
                        ele.classList.remove('subtitle-playing')
                    } catch {

                    }
                }
            }
            document.getElementById(newID).classList.add('subtitle-playing')
        },
        bookmarkPlayingID(newID, oldID) {
            if (oldID !== "") {
                var ele = document.getElementById(oldID)
                if (typeof ele != 'null') {
                    try {
                        ele.classList.remove('bookmark-playing')
                    } catch {

                    }
                }
            }
            document.getElementById(newID).classList.add('bookmark-playing')
        },
    },

    computed: {
        renameOption() {
            return !this.currentPath.endsWith('.varchive') && !this.currentPath.startsWith('/video/Recent')
                && !this.currentPath.startsWith('/video/All')
        },
        coverSrc() {
            if (typeof this.videoInfo === 'undefined' || typeof this.videoInfo.cover === 'undefined') {
                return ""
            }
            return this.isCoverMouseOver ? this.getRealImagSrc(this.videoInfo.cover.webp) : this.getRealImagSrc(this.videoInfo.cover.cover)
        },
        clips() {
            try {
                return this.videoInfo.previews.clips
            } catch (error) {
                console.log('This could be an expected exception:', error);
                return []
            }
        }
    },
    methods: {
        markraw(component) {
            return this.markRaw(component)
        },
        highlightTextWithMatch(inputText, pattern) {
            if (pattern === "") {
                return {
                    hasMatch: true,
                    highlightedText: inputText
                }
            }
            const regex = new RegExp(pattern, 'gi');
            const hasMatch = regex.test(inputText);

            var highlightedText = inputText
            if (hasMatch) {
                highlightedText = inputText.replace(regex, match => {
                    return `<span style="background-color: #409EFF; color:black;">${match}</span>`;
                });
            }
            // rgb(235, 180.6, 99);
            return {
                hasMatch: hasMatch,
                highlightedText: highlightedText
            }

        },
        getRealImagSrc(img) {
            if (typeof img === 'undefined') {
                return img
            }
            return img.at(0) === '/' ? img : this.webpPath + "/" + img
        },
        binarySearch(sortedArray, start, end, val, lessFunc) {
            if (start + 1 === end) {
                return lessFunc(val, sortedArray[start]) ? start : end
            }
            const mid = Math.floor((start + end) / 2)
            if (lessFunc(val, sortedArray[mid])) {
                return this.binarySearch(sortedArray, start, mid, val, lessFunc)
            } else {
                return this.binarySearch(sortedArray, mid, end, val, lessFunc)
            }
        },
        setSubShowing(subShowing) {
            this.subShowing = subShowing
        },
        setSubtitleInfoes(subtitleInfoes) {
            this.subtitleInfoes = subtitleInfoes
        },
        gotoPageByID(scrollContainerID, targetID) {
            var target = document.getElementById(targetID);
            var scrollContainer = document.getElementById(scrollContainerID);
            var offset = (scrollContainer.clientHeight - target.clientHeight) / 2
            scrollContainer.scrollTo({ top: target.offsetTop - scrollContainer.offsetTop - offset, behavior: "smooth" })
        },

        gotoSubPageByID(scrollContainerID, targetID) {
            if (!this.subPageInfo.isSubtitleMouseOver && !this.subPageInfo.isStopAutoScrollSub && this.subPageInfo.subPattern === "") {
                this.gotoPageByID(scrollContainerID, targetID)
            }
            this.subtitlePlayingID = targetID
        },

        gotoBookmarkPageByID(scrollContainerID, targetID) {
            if (!this.isBookmarksMouseOver) {
                this.gotoPageByID(scrollContainerID, targetID)
            }
            this.bookmarkPlayingID = targetID
        },

        async deleteVarchive() {
            ElMessageBox.confirm(
                'It will permanently delete the meta file and all varchive link files related to it. Continue?',
                'Warning',
                {
                    confirmButtonText: 'Delete',
                    cancelButtonText: 'Cancel',
                    type: 'warning',
                    icon: markRaw(Delete),
                }
            )
                .then(() => {
                    this.deleteVarchiveImple()
                })
                .catch(() => {
                })
        },

        async deleteVarchiveImple() {
            const url = config.server.concat(config.post.deleteVarchive)
            try {
                const response = await fetch(url, {
                    method: 'POST', headers: {
                        'Content-Type': 'application/json'
                    }, body: JSON.stringify({ "linkDir": this.currentPath })
                })
                if (!response.ok) {
                    const message = await response.json()
                    this.showElNotification('Error', message.detail, 'error')
                    return
                }
                ElMessage({
                    message: 'Deleted!',
                    type: 'success',
                })
                window.location.href = this.$route.path
            } catch (error) {
                console.log('Request Failed:', error);
                return
            }
        },

        async renameVarchiveLinkDir() {
            const url = config.server.concat(config.post.renameVarchive)
            try {
                const response = await fetch(url, {
                    method: 'POST', headers: {
                        'Content-Type': 'application/json'
                    }, body: JSON.stringify({ "srcLinkDir": this.currentPath, "dstLinkName": this.videoInfo.title })
                })
                if (!response.ok) {
                    const message = await response.json()
                    this.showElNotification('Error', message.detail, 'error')
                    return
                }
                ElMessage({
                    message: 'renamed!',
                    type: 'success',
                })
                const folders = this.currentPath.split('/')
                const newPath = folders.slice(0, folders.length - 1).join('/') + "/" + this.videoInfo.title
                window.location.href = newPath
            } catch (error) {
                console.log('Request Failed:', error);
                return
            }
        },

        async fetchInfo() {
            await new Promise((resolve) => {
                let timer = setInterval(() => {
                    if (this.webSocket.readyState === WebSocket.OPEN) {
                        resolve(true)
                        clearInterval(timer)
                        console.log("OPEN...")
                    }
                }, 100)
            }).then(res => { return })
            var urls = []
            for (var i = 0, len = this.videoInfo.path.length; i < len; ++i) {
                urls.push(this.videoInfo.path[i].url)
            }
            await this.sendMessage(JSON.stringify({ "type": ["server", "connection", this.currentPath], "message": JSON.stringify(urls) }))
            await this.sendMessage(JSON.stringify({
                "type": ["server", "bookmarks", "fetch"], "message": JSON.stringify(this.getMessageToServer())
            }))
            await this.sendMessage(JSON.stringify({
                "type": ["server", "statistics", "fetch"], "message": JSON.stringify(this.getMessageToServer())
            }))
        },
        async editBookmark(index, bookmark) {
            const message = this.getMessageToServer()
            message.timestamp = bookmark.timestamp
            message.index = index
            message.title = bookmark.title
            message.description = bookmark.description
            await this.sendMessage(JSON.stringify({
                "type": ["server", "bookmarks", "editing"],
                "message": JSON.stringify(message)
            }))
        },
        async removeBookmark(index, timestamp) {
            const message = this.getMessageToServer()
            message.timestamp = timestamp
            message.index = index
            await this.sendMessage(JSON.stringify({
                "type": ["server", "bookmarks", "remove"],
                "message": JSON.stringify(message)
            }))
        },
        async clearBookmarks() {
            ElMessageBox.confirm(
                'It will permanently delete all bookmarks. Continue?',
                'Warning',
                {
                    confirmButtonText: 'Delete',
                    cancelButtonText: 'Cancel',
                    type: 'warning',
                    icon: markRaw(Delete),
                }
            )
                .then(async () => {
                    const message = this.getMessageToServer()
                    await this.sendMessage(JSON.stringify({
                        "type": ["server", "bookmarks", "clear"],
                        "message": JSON.stringify(message)
                    }))
                })
                .catch(() => {
                })
        },
        getMessageToServer() {
            const message = {}
            // this.videoInfo.path[0].url
            message["currentURL"] = this.urlSelected
            message["varchiveCurrentPath"] = this.currentPath
            return message
        },
        async generatePreview() {
            await this.sendMessage(JSON.stringify({
                "type": ["server", "generate-preview"], "message": JSON.stringify(this.getMessageToServer())
            }))
        },
        async deletePreviews() {
            await this.sendMessage(JSON.stringify({
                "type": ["server", "clear-preview"], "message": JSON.stringify(this.getMessageToServer())
            }))
        },
        async loadElements() {
            this.cover = this.videoInfo.cover
            this.infoEditing["title"] = this.videoInfo.title
            this.infoEditing["description"] = this.videoInfo.description
            this.infoEditing["info"] = this.videoInfo.info
        },
        async changeInfo(newInfo) {
            newInfo.currentURL = this.urlSelected
            newInfo.varchiveCurrentPath = this.currentPath
            console.log("newInfo:", newInfo)
            const message = JSON.stringify({ "type": ["server", "info-editing"], "message": JSON.stringify(newInfo) })
            await this.sendMessage(message)
            this.isInfoEditing = false
        },
        async updateURL(newUrls) {
            const updateInfo = {}
            updateInfo.path = newUrls
            updateInfo.varchiveCurrentPath = this.currentPath
            updateInfo.currentURL = this.urlSelected
            console.log("newUrls:", updateInfo)
            const message = JSON.stringify({ "type": ["server", "info-editing"], "message": JSON.stringify(updateInfo) })
            await this.sendMessage(message)
        },
        async seekTo(seconds) {
            await this.sendMessage(this.genSeekCommand(seconds))
        },
        async openInIINA(url) {
            url = url.trim()
            if (url === "") {
                return
            }
            const openInIINAMessage = JSON.stringify({ "type": ["server", "openInIINA"], "message": url })
            await this.sendMessage(openInIINAMessage)
        },
        genSeekCommand(seconds) {
            return JSON.stringify({ "type": ["iina", "seek", this.urlSelected], "message": seconds.toString() })
        },
        showAlterBox(type, titile, message) {
            ElMessageBox.alert(message, titile, {
                confirmButtonText: 'OK',
                type: type,
            })
        },
        showElNotification(title, message, type) {
            ElNotification({
                title: title,
                message: message,
                type: type,
                // position: 'bottom-left',
                offset: 200,
            })
        },
        handleMessage(message) {
            switch (message.type[1]) {
                case "notification":
                    const messageBox = JSON.parse(message.message)
                    if (messageBox.boxType === "message") {
                        ElMessage({
                            message: messageBox.title,
                            type: messageBox.type,
                        })
                    } else if (messageBox.boxType === "notification") {
                        this.showElNotification(messageBox.title, messageBox.description, messageBox.type)
                    } else if (messageBox.boxType === "messageBox") {
                        thiis.showAlterBox(messageBox.type, messageBox.title, messageBox.description)
                    } else {

                    }
                    break;
                case "connection":
                    if (message.type[2] === "paired") {
                        this.connection = "iinaConnected"
                        this.showElNotification('Success', 'Connected with IINA.', 'success')
                    } else {
                        this.connection = "serverConnected"
                        this.showElNotification('Info', 'The connection with IINA is closed.', 'info')
                    }
                    break;
                case "playerInfo":
                    this.playerMessage = JSON.parse(message.message)
                    this.videoPos = this.playerMessage.pos
                    this.statistics = message.statistics
                    break;
                case "statistics":
                    if (message.type[2] === "info") {
                        this.statistics = JSON.parse(message.message)
                    } else {

                    }
                    break;
                case "bookmarks":
                    if (message.type[2] == "removed") {
                        this.bookmarkInfo = JSON.parse(message.message)
                        ElMessage({
                            message: 'Removed!',
                            type: 'success',
                        })
                    } else if (message.type[2] == "remove-error") {
                        this.showElNotification('Error', message.message, 'error')
                    }
                    else if (message.type[2] == "cleared") {
                        this.bookmarkInfo = JSON.parse(message.message)
                        ElMessage({
                            message: 'Cleared!',
                            type: 'success',
                        })
                    } else if (message.type[2] == "edited") {
                        this.bookmarkInfo = JSON.parse(message.message)
                        ElMessage({
                            message: 'Edited!',
                            type: 'success',
                        })
                    } else if (message.type[2] == "editing-error") {
                        this.showElNotification('Error', message.message, 'error')
                    }
                    else {
                        this.bookmarkInfo = JSON.parse(message.message)
                    }
                    this.isHideBookmarks = this.bookmarkInfo.bookmarks.length === 0
                    break;
                case "details":
                    const type2 = message.type[2]
                    if (type2 === "editing-error") {
                        this.showAlterBox('error', 'Error while editing information', message.message)
                        return
                    } else if (type2 === "preview-cleared") {
                        ElMessage({
                            message: 'Preview cleared!',
                            type: 'success',
                        })
                    }
                    else {
                        if (type2 === "edited") {
                            ElMessage({
                                message: 'Edited!',
                                type: 'success',
                            })
                        }
                    }
                    this.videoInfo = JSON.parse(message.message)
                    break;
                default:
                    break;
            }
        },
        async getWebsocketID() {
            const url = config.server.concat(config.get.websocketID)
            console.log(url)
            try {
                const response = await fetch(url)
                if (!response.ok) {
                    throw new Error(await response.text());
                }
                const resJson = await response.json()
                const id = JSON.parse(resJson.id)
                return id
            } catch (error) {
                console.log('Request Failed:', error);
                return -2
            }
        },
        async retryWebsocketConnection() {
            let timer = setTimeout(async () => {
                if (this.isBeforeUnmount) {
                    clearTimeout(timer)
                }
                else {
                    if (this.webSocket.readyState !== WebSocket.OPEN) {
                        clearTimeout(timer)
                        try {
                            await this.webSocketManager()
                        } catch (error) {
                            console.log('This could be an expected exception:', error);
                            return []
                        }
                    }
                }
            }, 3000)
        },
        async webSocketManager() {
            const id = await this.getWebsocketID()
            if (id === -2) {
                await this.retryWebsocketConnection()
                return
            }
            if (id === -1) {
                this.showAlterBox('error', "Error: Fetch websocketID.", "No ID available.")
                return
            }
            const wsUrl = config.wsServer.concat('/', id)
            this.webSocket = new WebSocket(wsUrl)
            this.webSocket.onopen = async (event) => {
                this.connection = "serverConnected"
                // this.showElNotification('Success', 'Connected with server.', 'success')
                await this.fetchInfo()
            }
            this.webSocket.onmessage = (event) => {
                const message = JSON.parse(event.data)
                this.handleMessage(message)
            }
            this.webSocket.onclose = async (event) => {
                this.connection = "closed"
                if (!this.isBeforeUnmount) {
                    this.showElNotification('Warning', 'Cannot connect to server. Retrying ...', 'warning')
                    await this.retryWebsocketConnection()
                }
            }
        },
        async sendMessage(message) {
            console.log("message:", message)
            await this.webSocket.send(message)
        },
        async loadInfo() {
            const res = await loadVideoInfo(this.$route.path)
            if (res.returnCode !== 0) {
                return
            }
            this.currentPath = res.currentPath
            this.videoPath = res.videoPath
            this.webpPath = res.webpPath
            this.videoInfo = res.videoInfo
            if (this.$route.path.startsWith('/video/Recent')) {
                const splits = this.webpPath.split('/')
                const metaFilename = splits[splits.length - 1]
                const path = "/video/All/".concat(metaFilename, "/details")
                window.location.href = path
            }
        },
        goToIntroduce() {
            document.getElementById("introduction").scrollIntoView({ behavior: 'smooth', block: 'start', inline: 'nearest' })
        },
        handlePlugin() {
            this.isPluginEnvironment = this.$route.query.isPluginEnvironment === "true"
        }
    },
    async created() {
        this.handlePlugin()
        await this.webSocketManager()
        await this.loadInfo()
        await this.loadElements()
        document.title = this.videoInfo.title
        if (!this.isPluginEnvironment) {
            this.goToIntroduce()
        }
    },
    async beforeUnmount() {
        this.isBeforeUnmount = true
        await this.webSocket.close()
        document.title = "Varchive"
    },
}

</script>