<template>
    <section id="previews" class="previews">
        <h2 @mouseover="isMouseOverPreview = true" @mouseout="isMouseOverPreview = false">Previews
            <el-icon v-show="isMouseOverPreview && isHidePreview" class="icon" style="margin-left: 8px">
                <View @click="isHidePreview = false" />
            </el-icon>
            <el-icon v-show="isMouseOverPreview && !isHidePreview" class="icon" style="margin-left: 8px">
                <Hide @click="isHidePreview = true" />
            </el-icon>
        </h2>
        <div v-show="!isHidePreview">
            <el-button-group class="ml-4" style="margin-bottom: 15px;">
                <el-button v-show="!isPlayPreview" :icon="VideoPlayRaw" @click="isPlayPreview = true">
                </el-button>
                <el-button v-show="isPlayPreview" :icon="VideoPauseRaw" @click="isPlayPreview = false">
                </el-button>
                <el-popconfirm confirm-button-text="Delete" cancel-button-text="No" :icon="WarningFilledRaw"
                    icon-color="#E6A23C" title="Delete all clips?" @confirm="deletePreviews" @cancel="">
                    <template #reference>
                        <el-button :icon="DeleteRaw">
                        </el-button>
                    </template>
                </el-popconfirm>
                <el-popconfirm confirm-button-text="Yes" cancel-button-text="No" icon-color="#909399"
                    title="Generate clips?" @confirm="generatePreview" @cancel="">
                    <template #reference>
                        <el-button :icon="FilmRaw">
                        </el-button>
                    </template>
                </el-popconfirm>
            </el-button-group>
            <div>
                <WebpPreview v-for="clip in clips" @click="seekTo(clip.startTime)" :key="clip" :webpPath="webpPath"
                    :clip="clip" :isPlay="isPlayPreview" />
            </div>
        </div>
    </section>
</template>

<script>
import WebpPreview from '@/components/WebpPreview.vue'
import { View, Hide, VideoPlay, VideoPause, WarningFilled, Delete, Film } from '@element-plus/icons-vue'
import { markRaw } from 'vue'

export default {
    data() {
        return {
            VideoPlayRaw: markRaw(VideoPlay),
            VideoPauseRaw: markRaw(VideoPause),
            WarningFilledRaw: markRaw(WarningFilled),
            DeleteRaw: markRaw(Delete),
            FilmRaw: markRaw(Film),
            isMouseOverPreview: false,
            isHidePreview: false,
            isPlayPreview: false,
        }
    },
    props: {
        webpPath: { type: String, required: true },
        videoInfo: { type: Object, required: true },
        getMessageToServer: { type: Function, required: true },
        sendMessage: { type: Function, required: true },
        seekTo: { type: Function, required: true },
    },
    components: { WebpPreview, View, Hide, },
    computed: {
        clips() {
            try {
                return this.videoInfo.previews.clips
            } catch (error) {
                console.log('This could be an expected exception:', error);
                return []
            }
        }
    },
    methods: {
        async deletePreviews() {
            await this.sendMessage(JSON.stringify({
                "type": ["server", "clear-preview"], "message": JSON.stringify(this.getMessageToServer())
            }))
        },
        async generatePreview() {
            await this.sendMessage(JSON.stringify({
                "type": ["server", "generate-preview"], "message": JSON.stringify(this.getMessageToServer())
            }))
        },
    }
}
</script>