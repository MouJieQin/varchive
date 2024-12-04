<template>
    <div v-show="isMatch" class="subtitle" @mouseover="isMouseover = true" @mouseout="isMouseover = false">
        <div class="timestamp" @click=seekTo(subtitleInfo.startTime)>{{ subtitleInfo.startTimeFormat }}
        </div>
        <div v-if="isPluginEnvironment" v-html="highlightedText" style="font-size: 12px;"></div>
        <div v-else v-html="highlightedText"></div>
    </div>
</template>

<script>

export default {
    data() {
        return {
            isMatch: true,
            highlightedText: this.subtitleInfo.text,
            isMouseover: false,
        }
    },
    props: {
        isPluginEnvironment: { type: Boolean, required: true },
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
    components: {},
}
</script>