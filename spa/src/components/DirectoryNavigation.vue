<template>
    <div v-show="isShow" class="dir-nav" tabindex="-1" @keydown="checkKeyDown" @keyup="checkKeyUp">
        <router-link v-for="folder in this.folders" :id="this.dirs[folder.filename]" :class="folder.type"
            :key="this.dirs[folder.filename]" @click="dirUpdate" @keydown="checkKeyDown" @keyup="checkKeyUp"
            @mouseover="mouseOverRouterLink = this.dirs[folder.filename]" @mouseout="mouseOverRouterLink = ''"
            :to="{ name: this.dirs[folder.filename] }">
            {{ folder.filename }}
        </router-link>
    </div>
    <router-view></router-view>
    <div>
        <Covers :routeName="currRouterName" :fileStatusCode="fileStatusCode" :folders="folders" />
    </div>
</template>

<script>
import { onBeforeRouteLeave } from 'vue-router'
import config from '@/config.json'
import Covers from '@/views/Covers.vue'
import { fileOperate } from '@/common/varchiveVideo.js'

export default {
    data() {
        return {
            fileStatusCode: 0,
            folders: [],
            dirs: [],
            mouseOverRouterLink: "",
            isMetaKeyDown: false,
            currRouterName: "",
        }
    },
    components: { Covers },
    computed: {
        isShow() { return this.$route.path !== "/video/Recent" && !this.$route.path.startsWith("/video/All") },
        hasRoute() {
            return this.dirs.length == 0
        }
    },
    methods: {
        async checkKeyDown(event) {
            if (event.key === 'f') {
                if (this.mouseOverRouterLink != "") {
                    await fileOperate(this.mouseOverRouterLink, "openInFinder")
                }
            } else if (event.key === 'Backspace') {
                if (this.mouseOverRouterLink != "") {
                    const res = await fileOperate(this.mouseOverRouterLink, "moveToTrash")
                    if (res.returnCode === 0) {
                        window.location.reload();
                    }
                }
            } else if (event.key === 'Meta') {
                this.isMetaKeyDown = true
            }
        },
        checkKeyUp(event) {
            if (event.key === 'Meta') {
                self.isMetaKeyDown = false
            }
        },
        async dirUpdate() {
            if (this.isMetaKeyDown) {
                return
            }
            var from = this.$route.name
            await new Promise((resolve) => {
                let timer = setInterval(() => {
                    resolve(true)
                    clearInterval(timer)
                }, 100)
            }).then(res => { return })

            var targetFolder = this.$route.name
            var splits = targetFolder.split('/')
            var parent = splits.slice(0, splits.length - 1).join('/')
            if (from === parent) {
                return
            }
            await this.$router.replace({ name: parent })
            await this.$router.push({ name: targetFolder })
        },
        async initData(currRouterName) {
            const url = config.server.concat(config.get.filemanager, "?path=", currRouterName)
            try {
                const response = await fetch(url)
                const resJson = await response.json()
                this.folders = resJson["fileList"]
                this.fileStatusCode = resJson["fileStatusCode"]
                switch (this.fileStatusCode) {
                    case -1:
                        throw new Error(currRouterName + " not exists!");
                    case 0:
                        this.$router.addRoute(currRouterName,
                            {
                                path: "details",
                                name: currRouterName.concat("/details"),
                                component: () => import('@/views/VideoDetails.vue'),
                                props: route => ({ ...route.params })
                            }
                        )
                        await this.$router.push({ name: currRouterName.concat("/details") })
                        return
                    case 1:
                        throw new Error(currRouterName + " is a file!");
                    case 2:
                    // It's a normal directory
                    default:
                        break
                }
            } catch (error) {
                console.log('Request Failed:', error);
                return
            }
            for (var i = 0, len = this.folders.length; i < len; ++i) {
                const childName = currRouterName.concat("/", this.folders[i].filename)
                this.dirs[this.folders[i].filename] = childName
                this.$router.addRoute(currRouterName,
                    {
                        path: this.folders[i].filename,
                        name: childName,
                        component: () => import('@/components/DirectoryNavigation.vue'),
                        props: route => ({ ...route.params })
                    }
                )
            }
        },
    },
    async created() {
        this.currRouterName = this.$route.name
        await this.initData(this.currRouterName)
        const slices = this.$route.name.split('/')
        document.title = slices[slices.length - 1]
    },
    beforeUnmount() {
        document.title = "Varchive"
    }
}
</script>
