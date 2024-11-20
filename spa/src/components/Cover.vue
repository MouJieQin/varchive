<template>
    <div class="gallery-cover">
        <router-link :to="{ name: this.getRouteName() }">
            <div class="image-container">
                <img @mouseover="mouseOver" @mouseout="mouseOut" :src="clipImgSrc()" :alt="clip.cover">
                <CollectionTag v-show="isMouseOver || isMouseOverOnBookmarkIcon" :id="`bookmark-icon-${videoPath}`"
                    class="image-icon" @mouseover="isMouseOverOnBookmarkIcon = true"
                    @mouseout="isMouseOverOnBookmarkIcon = false" @click.prevent="bookmarkClick" />
            </div>
            <div class="cover-title">
                <p>{{ videoInfo.title }}</p>
            </div>
        </router-link>
    </div>
</template>

<script>
import { loadBookmarks } from '@/common/varchiveVideo.js'
import { CollectionTag } from '@element-plus/icons-vue'

export default {
    data() {
        return {
            isMouseOver: false,
            isMouseOverOnBookmarkIcon: false,
            bookmarks: {},
            bookmarkClips: [{
                "webp": "/icons/landscape.png",
                "cover": "/icons/landscape.png",
                "startTime": 0,
                "endTime": 0,
            }],
            previewClips: [],
            isBookmarkLoad: false,
            isShowBookmark: false,
            clip: this.videoInfo.cover,
            clips: [],
            clipIndex: 0,
            timer: {},
        }
    },

    props: {
        videoPath: { type: String, required: true },
        videoInfo: { type: Object, required: true },
        routePath: { type: String, required: true },
        webpPath: { type: String, required: true },
        isPlay: { type: Boolean, required: true },
    },
    components: { CollectionTag },

    methods: {
        getRouteName() {
            return this.routePath.slice(1, this.routePath.length)
        },
        getRealImagSrc(img) {
            return img.at(0) === '/' ? img : this.webpPath + "/" + img
        },
        mouseOut() {
            this.isMouseOver = false
            clearInterval(this.timer)
            this.clip = this.videoInfo.cover
        },
        async mouseOver() {
            if (!this.isBookmarkLoad) {
                const res = await this.loadBookmark()
                if (res) {
                    this.isShowBookmark = true
                    this.clips = this.bookmarkClips
                    this.clipIndex = 0
                    document.getElementById('bookmark-icon-'.concat(this.videoPath)).style.color = '#F56C6C'
                }
            }

            this.isMouseOver = true
            if (this.clips.length === 0) {
                return
            }
            this.clip = this.clips[this.clipIndex]
            this.timer = setInterval(() => {
                if (this.clipIndex >= this.clips.length - 1) {
                    this.clipIndex = 0
                } else {
                    this.clipIndex += 1
                }
                this.clip = this.clips[this.clipIndex]
            }, 3000)
        },
        clipImgSrc() {
            if (this.isPlay) {
                return this.getRealImagSrc(this.clip.webp)
            } else {
                return this.isMouseOver ? this.getRealImagSrc(this.clip.webp) : this.getRealImagSrc(this.clip.cover)
            }
        },

        async bookmarkClick() {
            this.isShowBookmark = !this.isShowBookmark
            if (this.isShowBookmark) {
                this.clips = this.bookmarkClips
                this.clipIndex = 0
                document.getElementById('bookmark-icon-'.concat(this.videoPath)).style.color = '#F56C6C'
            } else {
                this.clips = this.previewClips
                this.clipIndex = 0
                document.getElementById('bookmark-icon-'.concat(this.videoPath)).style.color = 'white'
            }
        },

        async loadBookmark() {
            const res = await loadBookmarks(this.videoPath)
            this.isBookmarkLoad = true
            if (res.returnCode === 0) {
                this.bookmarks = res.bookmarks
                this.bookmarkClips = this.bookmarks.bookmarks.map((ele) => { return ele.clip })
                return true
            } else {
                return false
            }
        }
    },

    created() {
        this.previewClips = [].concat(this.videoInfo.cover, this.videoInfo.previews.clips)
        this.clips = this.previewClips
    },
    beforeUnmount() {
        clearInterval(this.timer)
    }

}
</script>