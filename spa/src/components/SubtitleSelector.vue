<template>
    <div class="flex flex-wrap items-center">
        <el-select v-model="selectedSub" placeholder="Subtitle" size="default"
            style="width: 100px; margin-top:20px; margin-bottom:20px;text-align: center">
            <el-option v-for="loadedSubtitle in loadedSubtitles" :key="loadedSubtitle" :id="loadedSubtitle"
                :label="loadedSubtitle" :value="loadedSubtitle" />
        </el-select>
    </div>
</template>

<script>
import { RefreshLeft } from '@element-plus/icons-vue'
import config from '@/config.json'

export default {
    data() {
        return {
            firstLoadingSub: true,
            selectedSub: "",
        }
    },
    props: {
        subtitleInfoes: { type: Object, required: true },
        subShowing: { type: String, required: true },
        loadedSubtitles: { type: Object, required: true },
        setSubtitleInfoes: { type: Function, required: true },
        setSubShowing: { type: Function, required: true },
    },
    components: { RefreshLeft },

    watch: {
        loadedSubtitles(newSubs, oldSubs) {
            if (typeof newSubs != 'undefined') {
                if (this.firstLoadingSub && newSubs.length !== 0 && this.selectedSub !== newSubs[-1]) {
                    this.firstLoadingSub = false
                    this.loadSubtitle(newSubs[newSubs.length - 1])
                }
            }
        },
        selectedSub(newSub, oldSub) {
            this.loadSubtitle(newSub)
        }
    },

    methods: {
        async clearPlayingClass() {
            for (var i = 0, len = this.subtitleInfoes.length; i < len; ++i) {
                var ele = document.getElementById(this.subShowing.concat('-', this.subtitleInfoes[i].startTimeFormat))
                ele.classList.remove('subtitle-playing')
            }
        },
        async loadSubtitle(loadedSubtitle) {
            this.selectedSub = loadedSubtitle
            const url = config.server.concat(config.get.subtitleParse, "?path=", loadedSubtitle)
            try {
                const response = await fetch(url)
                const resJson = await response.json()
                if (resJson.subParseCode != 0) {
                    throw new Error(resJson.subParsedJsonStr);
                } else {
                    this.setSubtitleInfoes(JSON.parse(resJson.subParsedJsonStr))
                    this.setSubShowing(loadedSubtitle)
                }
            } catch (error) {
                console.log('Request Failed:', error);
                return
            }
            this.clearPlayingClass()
        }
    }
}
</script>