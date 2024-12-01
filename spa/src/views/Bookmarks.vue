<template>
    <section id="bookmarks" class="bookmarks">
        <h2 @mouseover="isMouseoverBookmarks = true" @mouseout="isMouseoverBookmarks = false">Bookmarks
            <el-icon v-show="isMouseoverBookmarks && isHideBookmarks" class="icon" style="margin-left: 8px">
                <View @click="isHideBookmarks = false" />
            </el-icon>
            <el-icon v-show="isMouseoverBookmarks && !isHideBookmarks" class="icon" style="margin-left: 8px">
                <Hide @click="isHideBookmarks = true" />
            </el-icon>
        </h2>
        <div v-show="!isHideBookmarks">
            <div style="margin-bottom: 30px;">
                <el-input v-model="bookmarkPattern" clearable style="max-width: 600px;margin-bottom: 10px;float:right">
                    <template #append>
                        <el-icon>
                            <Search />
                        </el-icon>
                    </template>
                </el-input>
                <div style="margin-bottom: 15px;">
                    <el-button-group class="ml-4">
                        <el-button v-show="!isPlayBookmarks" :icon="VideoPlayRaw" @click="isPlayBookmarks = true">
                        </el-button>
                        <el-button v-show="isPlayBookmarks" :icon="VideoPauseRaw" @click="isPlayBookmarks = false">
                        </el-button>
                        <el-button :icon="DeleteRaw" @click="clearBookmarks">
                        </el-button>
                        <el-button v-show="!isWebpsOnly" :icon="GridRaw" @click="isWebpsOnly = true">
                        </el-button>
                        <el-button v-show="isWebpsOnly" :icon="ListRaw" @click="isWebpsOnly = false">
                        </el-button>
                    </el-button-group>
                </div>
            </div>
            <div v-show="isWebpsOnly">
                <WebpPreview v-for="bookmark in bookmarkInfo.bookmarks" @click="seekTo(bookmark.timestamp)"
                    :key="bookmark.format" :webpPath="webpPath" :clip="bookmark.clip" :isPlay="isPlayBookmarks" />
            </div>
            <div v-show="!isWebpsOnly" class="scroll-container" id="bookmarks-scroll-container">
                <Bookmark v-for="(bookmark, index) in bookmarkInfo.bookmarks" :key="bookmark.format"
                    @mouseover="isBookmarksMouseOver = true" @mouseout="isBookmarksMouseOver = false"
                    :id="`bookmark-${bookmark.timestamp.toString()}`" :seekTo="seekTo" :webpPath="webpPath"
                    :bookmark="bookmark" :index="index" :removeBookmark="removeBookmark"
                    :bookmarkPattern="bookmarkPattern" :highlightTextWithMatch="highlightTextWithMatch"
                    :editBookmark="editBookmark" :isPlayBookmarks="isPlayBookmarks" />
            </div>
        </div>
    </section>
</template>

<script>
import Bookmark from '@/components/Bookmark.vue'
import WebpPreview from '@/components/WebpPreview.vue'
import { VideoPlay, VideoPause, Delete, Grid, List, View, Hide, Search } from '@element-plus/icons-vue'
import { markRaw } from 'vue'

export default {
    data() {
        return {
            VideoPlayRaw: markRaw(VideoPlay),
            VideoPauseRaw: markRaw(VideoPause),
            DeleteRaw: markRaw(Delete),
            GridRaw: markRaw(Grid),
            ListRaw: markRaw(List),
            isPlayBookmarks: false,
            isMouseoverBookmarks: false,
            isHideBookmarks: false,
            isWebpsOnly: false,
            isBookmarksMouseOver: false,
            bookmarkPattern: "",
        }
    },
    watch: {
        isBookmarksMouseOver(newVal, oldVal) {
            this.setIsBookmarksMouseOver(newVal)
        }
    },
    props: {
        setIsBookmarksMouseOver: { type: Function, required: true },
        clearBookmarks: { type: Function, required: true },
        bookmarkInfo: { type: Object, required: true },
        seekTo: { type: Function, required: true },
        removeBookmark: { type: Function, required: true },
        highlightTextWithMatch: { type: Function, required: true },
        editBookmark: { type: Function, required: true },
        webpPath: { type: String, required: true },
    },
    components: { WebpPreview, Bookmark, View, Hide, Search },
    computed: {
    },
    methods: {
    }
}
</script>