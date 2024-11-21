<template>
    <el-dialog v-model="isDialogVisible" title="Shipping address" width="500">
        <p>Tasks: {{ tasks }}</p>
        <p>IINA connections: {{ iinaConnections }}</p>
        <p>Varchive connections: {{ varchiveConnections }}</p>
        <el-switch v-model="shutdownInstantChecked" class="mb-2"
            style="--el-switch-on-color: #ff4949; --el-switch-off-color: #13ce66" active-text="Shutdown instantly"
            inactive-text="Shutdown after tasks are done" />
        <template #footer>
            <div class="dialog-footer">
                <el-button @click="isDialogVisible = false">Cancel</el-button>
                <el-button v-loading.fullscreen.lock="fullscreenLoading" type="primary" @click="handleExit">
                    Exit
                </el-button>
            </div>
        </template>
    </el-dialog>
</template>

<script>
import { serverOperate } from '@/common/varchiveVideo.js'
import { ElSwitch } from "element-plus";


export default {
    data() {
        return {
            shutdownInstantChecked: false,
            isDialogVisible: this.dialogVisible,
            tasks: 0,
            iinaConnections: 0,
            varchiveConnections: 0,
            updateTimer: {},
            fullscreenLoading: false,
        }
    },
    props: {
        dialogVisible: { type: Boolean, Required: true },
        setDialogVisible: { type: Function, Required: true },
    },
    watch: {
        dialogVisible(newVal, oldVal) {
            if (newVal) {
                this.isDialogVisible = newVal
            }
        },
        async isDialogVisible(newVal, oldVal) {
            this.setDialogVisible(newVal)
            if (newVal) {
                await this.updateServerInfo()
                this.updateTimer = setInterval(async () => {
                    await this.updateServerInfo()
                }, 1000)
            } else {
                clearInterval(this.updateTimer)
            }
        }
    },
    methods: {
        openFullScreen() {
            this.fullscreenLoading = true
            setTimeout(() => {
                this.fullscreenLoading = false
                this.refreshWindow()
            }, 5000)
        },
        refreshWindow() {
            window.location.reload();
        },
        async handleExit() {
            this.openFullScreen()
            if (this.shutdownInstantChecked) {
                const res = await serverOperate(["shutdown", "instant"])
                if (res.returnCode !== 0) {
                    return
                }
            } else {
                const res = await serverOperate(["shutdown", "default"])
                if (res.returnCode !== 0) {
                    return
                }
            }
        },
        async updateServerInfo() {
            const res = await serverOperate(["info"])
            if (res.returnCode !== 0) {
                return
            }
            const serverInfo = res.json
            this.tasks = serverInfo.tasks
            this.iinaConnections = serverInfo.iinaConnections
            this.varchiveConnections = serverInfo.varchiveConnections
        },
    }
}
</script>
