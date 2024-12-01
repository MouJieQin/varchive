<template>
    <section id="subtitles" class="subtitles">
        <h2 @mouseover="isMouseoverSubtitles = true" @mouseout="isMouseoverSubtitles = false">Subtitle
            <el-icon v-show="isMouseoverSubtitles && isHideSubtitles" class="icon" style="margin-left: 8px">
                <View @click="isHideSubtitles = false" />
            </el-icon>
            <el-icon v-show="isMouseoverSubtitles && !isHideSubtitles" class="icon" style="margin-left: 8px">
                <Hide @click="isHideSubtitles = true" />
            </el-icon>
        </h2>
        <div v-show="!isHideSubtitles">
            <div>
                <el-input v-model="subPageInfo.subPattern" clearable style="max-width: 600px;float:right">
                    <template #append>
                        <el-icon>
                            <Search />
                        </el-icon>
                    </template>
                </el-input>
                <el-button v-show="subPageInfo.isStopAutoScrollSub" :icon="RefreshLeftRaw"
                    @click="subPageInfo.isStopAutoScrollSub = false" style="clear:both">
                </el-button>
                <SubtitleSelector :loadedSubtitles="playerMessage.loadedSubtitles" :subtitleInfoes="subtitleInfoes"
                    :subShowing="subShowing" :setSubtitleInfoes="setSubtitleInfoes" :setSubShowing="setSubShowing" />
            </div>
            <div class="scroll-container" id="subtitle-scroll-container"
                @mouseover="subPageInfo.isStopAutoScrollSub = true; subPageInfo.isSubtitleMouseOver = true"
                @mouseout="subPageInfo.isSubtitleMouseOver = false">
                <Subtitle v-for="subtitleInfo in subtitleInfoes" :key="subtitleInfo"
                    :id="`${subShowing}-${subtitleInfo.startTimeFormat}`" :subtitleInfo="subtitleInfo"
                    :subPattern="subPageInfo.subPattern" :highlightTextWithMatch="highlightTextWithMatch"
                    :seekTo="seekTo" />
            </div>
        </div>
    </section>
</template>

<script>
import SubtitleSelector from '@/components/SubtitleSelector.vue'
import Subtitle from '@/components/Subtitle.vue'
import { RefreshLeft, View, Hide, Search } from '@element-plus/icons-vue'
import { markRaw } from 'vue'

export default {
    data() {
        return {
            RefreshLeftRaw: markRaw(RefreshLeft),
            isMouseoverSubtitles: false,
            isHideSubtitles: false,
            // isStopAutoScrollSub: false,
            // isSubtitleMouseOver: false,
            // subPattern: "",
        }
    },
    watch: {

    },
    props: {
        subPageInfo: { type: Object, required: true },
        playerMessage: { type: Object, required: true },
        subtitleInfoes: { type: Object, required: true },
        subShowing: { type: String, required: true },
        setSubtitleInfoes: { type: Function, required: true },
        setSubShowing: { type: Function, required: true },
        highlightTextWithMatch: { type: Function, required: true },
        seekTo: { type: Function, required: true },
    },
    components: { SubtitleSelector, Subtitle, View, Hide, Search },
    computed: {
    },
    methods: {
    }
}
</script>