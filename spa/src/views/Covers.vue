<template>
    <div id="gallery" v-if="isShow">
        <div :id="`gallery-${routeName}`">
            <section class="gallery">
                <p>Totoal:{{ varchiveVideos.length }}</p>
                <ul v-infinite-scroll="load" class="infinite-list" style="overflow:visible">
                    <li v-for="video in varchiveVideosShowing" :key="video" class="infinite-list-item">
                        <Cover :videoPath="videoInfos[video].videoPath" :videoInfo="videoInfos[video].videoInfo"
                            :routePath="getRoutePath(video)" :webpPath="videoInfos[video].webpPath" :isPlay="false" />
                    </li>
                </ul>
            </section>
        </div>
        <el-backtop :bottom="20" />
    </div>
</template>

<script>
import { loadVideoInfo } from '@/common/varchiveVideo.js'
import Cover from '@/components/Cover.vue'

export default {
    data() {
        return {
            varchiveVideosShowing: [],
            varchiveVideos: [],
            videoInfos: {},
            timer: {},
        }
    },
    components: { Cover },
    props: {
        routeName: { type: String, Required: true },
        fileStatusCode: { type: Number, Required: true },
        folders: { type: Array, Required: true }
    },
    watch: {
        async folders(newFolder, old) {
            this.initData()
            await this.loadInfo()
        }
    },
    computed: {
        isShow() {
            return this.routeName === this.$route.name && this.varchiveVideos.length !== 0
        }
    },
    methods: {
        load() {
            if (this.varchiveVideos.length) {
                var count = 28
                for (var i = this.varchiveVideosShowing.length, len = this.varchiveVideos.length; i < len && count > 0; --count, ++i) {
                    this.varchiveVideosShowing.push(this.varchiveVideos[i])
                }
            }
        },
        initData() {
            this.varchiveVideos = []
            if (this.fileStatusCode === 2) {
                const varchiveFolders = this.folders.filter((ele) => {
                    return ele.type === "varchive-video"
                })
                for (var i = 0, len = varchiveFolders.length; i < len; ++i) {
                    this.varchiveVideos.push(varchiveFolders[i].filename)
                }
            }
        },
        getRoutePath(folerName) {
            return this.$route.path.concat('/', folerName)
        },
        async loadInfo() {
            this.videoInfos = {}
            for (var i = 0, len = this.varchiveVideos.length; i < len; ++i) {
                const routePath = this.getRoutePath(this.varchiveVideos[i])
                const res = await loadVideoInfo(routePath.concat('/details'))
                if (res.returnCode === 0) {
                    this.videoInfos[this.varchiveVideos[i]] = {}
                    this.videoInfos[this.varchiveVideos[i]].currentPath = res.currentPath
                    this.videoInfos[this.varchiveVideos[i]].videoPath = res.videoPath
                    this.videoInfos[this.varchiveVideos[i]].webpPath = res.webpPath
                    this.videoInfos[this.varchiveVideos[i]].videoInfo = res.videoInfo
                }
            }
        },
        goToGallery() {
            const ele = document.getElementById("gallery-".concat(this.routeName))
            if (ele === null) {
                return false
            }
            ele.scrollIntoView({ behavior: 'smooth', block: 'start', inline: 'nearest' })
            return true
        }
    },
    created() {
        var count = 0
        this.timer = setInterval(() => {
            if (!this.isShow) {
                clearInterval(this.timer)
            } else {
                if (this.goToGallery()) {
                    count += 1
                    if (count == 3) {
                        clearInterval(this.timer)
                    }
                }
            }
        }, 500)
    },
    beforeUnmount() {
        clearInterval(this.timer)
    }
}
</script>
