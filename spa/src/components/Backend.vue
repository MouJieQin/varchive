<template>
    <el-dialog v-model="isDialogVisible" title="Backend" width="500">
        <div v-if="isConnectServer">
            <p>Tasks: {{ tasks }}</p>
            <p>IINA connections: {{ iinaConnections }} </p>
            <p>Varchive connections: {{ varchiveConnections }}</p>
            <p>Is shutdown in tasks: {{ isShutdownInTasks }}</p>
            <el-switch v-model="shutdownInstantChecked" class="mb-2"
                style="--el-switch-on-color: #ff4949; --el-switch-off-color: #13ce66" active-text="Shutdown now"
                inactive-text="Shutdown after tasks are done" />
        </div>
        <div v-else>
            <h1>Cannot connect to server.</h1>
        </div>
        <template #footer v-if="isConnectServer">
            <div class="dialog-footer">
                <el-button v-if="isLockShutdown" type="primary" :icon="LockComponent"
                    @click="handleLockShutdown">Shutdown</el-button>
                <el-button v-else :icon="UnlockComponent" @click="handleLockShutdown">Shutdown</el-button>
                <el-button v-if="tasks !== 0" @click="cancelAllTasks">Cancel All Tasks</el-button>
                <el-button v-if="isShutdownInTasks" type="primary" @click="cancelShutdown">Cancel
                    Shutdown</el-button>
                <el-button @click="isDialogVisible = false">Cancel</el-button>
                <el-button id="shutdown-server-button" :icon="SwitchButtonRaw"
                    v-loading.fullscreen.lock="fullscreenLoading" type="danger" @click="handleShutdown"
                    :disabled="isLockShutdown">
                    ShutDown
                </el-button>
            </div>
        </template>
    </el-dialog>
</template>

<script>
import { serverOperate } from '@/common/varchiveVideo.js'
import { ElSwitch, ElMessage } from "element-plus"
import { Unlock, Lock, SwitchButton } from '@element-plus/icons-vue'
import { markRaw } from 'vue'

export default {
    data() {
        return {
            UnlockComponent: markRaw(Unlock),
            LockComponent: markRaw(Lock),
            SwitchButtonRaw: markRaw(SwitchButton),
            isLockShutdown: false,
            isConnectServer: true,
            shutdownInstantChecked: false,
            isDialogVisible: this.dialogVisible,
            tasks: 0,
            iinaConnections: 0,
            varchiveConnections: 0,
            isShutdownInTasks: false,
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
        async handleLockShutdown() {
            const newVal = !this.isLockShutdown
            await serverOperate(["shutdown", newVal ? "lock" : "unlock"])
        },
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
        async handleShutdown() {
            if (this.shutdownInstantChecked) {
                this.openFullScreen()
                await serverOperate(["shutdown", "instant"])
            } else {
                if (this.tasks === 0) {
                    this.openFullScreen()
                }
                await serverOperate(["shutdown", "default"])
            }
        },
        async cancelAllTasks() {
            const res = await serverOperate(["task", "cancelAll"])
            if (res.returnCode === 0) {
                return
            } else {
                ElMessage({
                    message: "Cancel failed!",
                    type: "error",
                });
            }
        },
        async cancelShutdown() {
            const res = await serverOperate(["shutdown", "cancel"])
            if (res.returnCode === 0) {
                return
            } else {
                ElMessage({
                    message: "Cancel failed!",
                    type: "error",
                });
            }
        },
        async updateServerInfo() {
            const res = await serverOperate(["info"])
            if (res.returnCode !== 0) {
                this.isConnectServer = false
                return
            } else {
                this.isConnectServer = true
                const serverInfo = res.json
                this.tasks = serverInfo.tasks
                this.iinaConnections = serverInfo.iinaConnections
                this.varchiveConnections = serverInfo.varchiveConnections
                this.isShutdownInTasks = serverInfo.isShutdownInTasks
                this.isLockShutdown = serverInfo.isLockShutdown
            }
        },
    }
}
</script>
