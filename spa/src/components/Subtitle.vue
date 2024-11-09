<template>
    <div v-show="isMatch" class="subtitle" @mouseover="isMouseover = true" @mouseout="isMouseover = false">
        <div class="timestamp">{{ subtitleInfo.startTimeFormat }}
            <el-icon v-show="isMouseover" class="icon" style="margin-left: 15px">
                <Back @click="seekTo(subtitleInfo.startTime)" />
            </el-icon>
        </div>
        <div v-html="highlightedText"></div>
    </div>
</template>

<script>

import WebpPreview from '@/components/WebpPreview.vue'
import { Back } from '@element-plus/icons-vue'

export default {
    data() {
        return {
            isMatch: true,
            highlightedText: this.subtitleInfo.text,
            isMouseover: false,
        }
    },
    props: {
        subtitleInfo: { type: Object, required: true },
        subPattern: { type: String, required: true },
        highlightTextWithMatch: { type: Function, required: true },
        seekTo: { type: Function, required: true }
    },
    watch: {
        subPattern(newPattern, old) {
            const result = this.highlightTextWithMatch(this.subtitleInfo.text, this.subPattern)
            this.isMatch = result.hasMatch
            this.highlightedText = result.highlightedText
        },
    },
    components: { Back },
}
</script>