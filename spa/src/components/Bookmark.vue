<template>
    <div v-show="isMatch" class="bookmark" @mouseover="isMouseOver = true" @mouseout="isMouseOver = false">
        <!-- <div class="timestamp">{{ bookmark.format }}</div> -->
        <div>
            <WebpPreview @click="seekTo(bookmark.timestamp)" :webpPath="webpPath" :clip="bookmark.clip"
                :isPlay="isPlayBookmarks" style="margin-right: 30px;"/>
        </div>
        <div>
            <div v-show="isMouseOver" style="margin-bottom: 20px;">
                <el-popconfirm confirm-button-text="Delete" cancel-button-text="No" icon-color="#E6A23C"
                    title="Delete this bookmark?" @confirm="removeBookmark(index, bookmark.timestamp)" @cancel="">
                    <template #reference>
                        <el-icon class="icon" style="margin-left: 15px">
                            <Delete />
                        </el-icon>
                    </template>
                </el-popconfirm>

                <el-icon v-show="!isEditingBookmark" class="icon" style="margin-left: 15px; float:left">
                    <Edit @click="isEditingBookmark = true" />
                </el-icon>
                <el-icon v-show="!isEditingBookmark" class="icon" style="margin-left: 15px; float:left">
                    <CopyDocument @click="copyBookmark" />
                </el-icon>
                <el-icon v-show="isEditingBookmark" class="icon" style="margin-left: 15px; float:left">
                    <Close @click="isEditingBookmark = false" />
                </el-icon>
                <el-icon v-show="isEditingBookmark" class="icon" style="margin-left: 15px; float:left">
                    <Check @click="handleEditBookmark(index, bookmarkForEditing)" />
                </el-icon>
            </div>
            <h3 v-if="!isEditingBookmark" v-html="highlightedTitle"></h3>
            <el-input v-else v-model="bookmarkForEditing.title" clearable style="margin-bottom: 10px;max-width: 600px">
                <template #prepend>Title</template>
            </el-input>
            <p class="editing" v-if="!isEditingBookmark" v-html="highlightedDescription"></p>
            <el-input v-else v-model="bookmarkForEditing.description" autosize type="textarea"
                style="margin-bottom: 10px;" />
        </div>
    </div>
</template>

<script>
import WebpPreview from '@/components/WebpPreview.vue'
import { CopyDocument, Check, Close, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import MarkdownIt from 'markdown-it'

export default {
    data() {
        return {
            isEditingBookmark: false,
            bookmarkForEditing: JSON.parse(JSON.stringify(this.bookmark)),
            isMouseOver: false,
            isMatch: true,
            highlightedTitle: this.bookmark.title,
            markdownParser: new MarkdownIt(),
            highlightedDescription: this.bookmark.description,
        }
    },
    props: {
        bookmark: { type: Object, required: true },
        index: { type: Number, required: true },
        seekTo: { type: Function, required: true },
        removeBookmark: { type: Function, required: true },
        editBookmark: { type: Function, required: true },
        webpPath: { type: String, required: true },
        isPlayBookmarks: { type: Boolean, required: true },
        bookmarkPattern: { type: String, required: true },
        highlightTextWithMatch: { type: Function, required: true }
    },
    components: { CopyDocument, Delete, Edit, Check, Close, WebpPreview, },

    watch: {
        bookmarkPattern(newPattern, old) {
            this.watchChange()
        },
        bookmark(newBookmark, old) {
            this.watchChange()
        },
    },

    methods: {
        watchChange() {
            if (this.bookmarkPattern === "") {
                this.isMatch = true
                this.highlightedTitle = this.bookmark.title
                this.highlightedDescription = this.markdownParser.render(this.bookmark.description)
            } else {
                const titleResult = this.highlightTextWithMatch(this.bookmark.title, this.bookmarkPattern)
                this.highlightedTitle = titleResult.highlightedText
                const descriptionResult = this.highlightTextWithMatch(this.bookmark.description, this.bookmarkPattern)
                this.highlightedDescription = descriptionResult.highlightedText
                this.isMatch = titleResult.hasMatch || descriptionResult.hasMatch
            }

        },
        handleEditBookmark(index, bookmarkForEditing) {
            this.editBookmark(index, bookmarkForEditing)
            this.isEditingBookmark = false
        },

        copyBookmark() {
            navigator.clipboard.writeText(this.bookmark.title.concat("\n", this.bookmark.description))
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
    },
    mounted() {
        this.watchChange()
    }
}
</script>