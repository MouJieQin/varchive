<template>
    <div style="display: flex; align-items: center;">
        <el-select v-model="selectedURL" placeholder="URL" size="default"
            style="width: 100px; margin-top:20px; margin-bottom:20px;text-align: center">
            <el-option v-for="path in paths" :key="path.url" :label="path.url" :value="path.url" />
        </el-select>
        <el-icon v-if="!isEditing" class="icon" style="margin-left: 10px">
            <Edit @click="isEditing = true" />
        </el-icon>
    </div>
    <div v-if="isEditing">
        <div style="margin-bottom: 15px;">
            <el-icon class="icon" style="margin-left: 15px">
                <Close @click="isEditing = false" />
            </el-icon>
            <el-icon class="icon" style="margin-left: 15px">
                <Check @click="handleUpdateURL" />
            </el-icon>
            <el-icon class="icon" style="margin-left: 15px">
                <Plus @click="addUrl" />
            </el-icon>
        </div>
        <div v-for="(url, index) in urls" style="margin-bottom: 10px;">
            <el-input v-model="url.url" clearable style="max-width: 600px">
                <template #prepend>URL</template>
                <template #append>
                    <el-icon class="icon" @click="copyURL(url.url)">
                        <CopyDocument />
                    </el-icon>
                    <el-icon class="icon" @click="deleteURL(index)" style="margin-left: 8px">
                        <Delete />
                    </el-icon>
                    <el-icon class="icon" @click="playInIINA(url.url)" style="margin-left: 8px">
                        <VideoPlay />
                    </el-icon>
                </template>
            </el-input>
        </div>
    </div>
</template>

<script>
import { CopyDocument, Plus, Check, Close, Edit, Refresh, Delete, VideoPlay, } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus';
export default {
    data() {
        return {
            isEditing: false,
            urls: JSON.parse(JSON.stringify(this.paths)),
            // urls: typeof this.paths !== 'undefined' ? JSON.parse(JSON.stringify(this.paths)) : {},
            selectedURL: "",
        }
    },
    props: {
        paths: { type: Object, required: true },
        openInIINA: { type: Function, required: true },
        setSeletedURL: { type: Function, required: true },
        updateURL: { type: Function, required: true }
    },
    watch: {
        paths(newPaths, old) {
            this.initUrlSelected()
        },
        selectedURL(newUrl, oldUrl) {
            this.setSeletedURL(newUrl)
        }
    },
    components: { CopyDocument, Plus, Check, Close, Edit, Refresh, Delete, VideoPlay },
    methods: {
        async playInIINA(url) {
            await this.openInIINA(url)
        },
        addUrl() {
            this.urls.push({ "url": "", "isSelected": false })
        },
        copyURL(url) {
            navigator.clipboard.writeText(url)
                .then(
                    () => {
                        ElMessage({
                            message: 'Copied!',
                            type: 'success',
                        })
                    }
                )
                .catch(err => {
                    ElMessage.error('Something went wrong', err)
                })
        },
        deleteURL(index) {
            this.urls.splice(index, 1)
        },
        handleUpdateURL() {
            this.urls = this.urls.filter((path) => { return path.url.trim() !== "" })
            this.updateURL(this.urls)
            this.isEditing = false
        },
        initUrlSelected() {
            // if (typeof this.paths === 'undefined') {
            //     this.selectedURL = ""
            //     return
            // }
            for (var i = 0, len = this.paths.length; i < len; ++i) {
                if (this.paths[i].isSelected) {
                    this.selectedURL = this.paths[i].url
                    return
                }
            }
            this.selectedURL = this.paths.lenght !== 0 ? this.paths[0].url : ""
        }
    },
    async mounted() {
        this.initUrlSelected()
    }
}
</script>
