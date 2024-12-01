<template>
    <section id="introduction" class="introduction">
        <div style="display: flex; align-items: center; margin-bottom:10px">
            <el-button-group class="ml-4">
                <el-button v-if="!isInfoEditing" :icon="EditRaw" style="" @click="isInfoEditing = true">
                </el-button>
                <el-button v-if="isInfoEditing" :icon="CloseRaw" @click="isInfoEditing = false">
                </el-button>
                <el-button v-if="isInfoEditing" :icon="CheckRaw"
                    @click="() => { changeInfo(infoEditing); isInfoEditing = false }">
                </el-button>
            </el-button-group>
        </div>
        <div class="title">
            <h1 v-if="!isInfoEditing" style="text-align: center;">{{ videoInfo.title }}
                <el-icon v-if="renameOption" class="icon" style="margin-left: 8px">
                    <Refresh @click="renameVarchiveLinkDir" />
                </el-icon>
            </h1>
            <el-input v-if="isInfoEditing" v-model="infoEditing.title" clearable
                style="margin-bottom: 10px;max-width: 40%">
                <template #prepend>Title</template>
            </el-input>
        </div>
        <div class="header">
            <img class="cover" @click="openInIINA(urlSelected)" @mouseover="isCoverMouseOver = true"
                @mouseout="isCoverMouseOver = false" :src="coverSrc" alt="cover">
            <p class="editing" v-if="!isInfoEditing" v-html="videoInfo.description"></p>
            <el-input v-else v-model="infoEditing.description" autosize type="textarea"
                placeholder="Please input description" />
        </div>

        <VideoURL :paths="videoInfo.path" :openInIINA="openInIINA" :setSeletedURL="setSeletedURL"
            :updateURL="updateURL" />

        <p class="editing" v-if="!isInfoEditing" v-html="videoInfo.info"></p>
        <el-input v-else v-model="infoEditing.info" autosize type="textarea" style="margin-bottom: 10px;"
            placeholder="Please input more information" />
    </section>
</template>

<script>
import VideoURL from '@/components/VideoURL.vue'
import { Edit, Close, Check, Refresh } from '@element-plus/icons-vue'
import { markRaw } from 'vue'

export default {
    data() {
        return {
            CheckRaw: markRaw(Check),
            CloseRaw: markRaw(Close),
            EditRaw: markRaw(Edit),
            isInfoEditing: false,
            isCoverMouseOver: false,
        }
    },
    props: {
        changeInfo: { type: Function, required: true },
        renameOption: { type: Function, required: true },
        openInIINA: { type: Function, required: true },
        getRealImagSrc: { type: Function, required: true },
        setSeletedURL: { type: Function, required: true },
        updateURL: { type: Function, required: true },
        renameVarchiveLinkDir: { type: Function, required: true },
        infoEditing: { type: Object, required: true },
        videoInfo: { type: Object, required: true },
        urlSelected: { type: String, required: true },
    },
    components: { VideoURL, Refresh },
    computed: {
        coverSrc() {
            if (typeof this.videoInfo === 'undefined' || typeof this.videoInfo.cover === 'undefined') {
                return ""
            }
            return this.isCoverMouseOver ? this.getRealImagSrc(this.videoInfo.cover.webp) : this.getRealImagSrc(this.videoInfo.cover.cover)
        },
    },
    methods: {

    }
}
</script>