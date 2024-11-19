<template>
    <div id="gallery" v-if="isShow">
        <section class="gallery">
            <div v-for="video in varchiveVideos" :key="video">
                <Cover :videoPath="videoInfos[video].videoPath" :videoInfo="videoInfos[video].videoInfo"
                    :routePath="getRoutePath(video)" :webpPath="videoInfos[video].webpPath" :isPlay="false" />
            </div>
        </section>
        <el-backtop :bottom="20" />
    </div>
</template>

<script>
import { loadVideoInfo } from '@/common/varchiveVideo.js'
import Cover from '@/components/Cover.vue'

export default {
    data() {
        return {
            varchiveVideos: [],
            videoInfos: {},
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
    },
}
</script>