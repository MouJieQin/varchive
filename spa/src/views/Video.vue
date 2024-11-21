<template>
    <div class="dir-nav" tabindex="-1" @keydown="checkKeyDown" @keyup="checkKeyUp">
        <router-link @click="dirUpdate" v-for="folder in this.lastFolders" :id="this.dirs[folder.filename]"
            :class="folder.type" :key="this.dirs[folder.filename]" @keydown="checkKeyDown" @keyup="checkKeyUp"
            @mouseover="mouseOverRouterLink = this.dirs[folder.filename]" @mouseout="mouseOverRouterLink = ''"
            :to="{ name: this.dirs[folder.filename] }">
            {{ folder.filename }}
        </router-link>
    </div>
    <router-view></router-view>
</template>

<script>
import { onBeforeRouteLeave } from 'vue-router'
import DirectoryNavigation from '@/components/DirectoryNavigation.vue'
import config from '@/config.json'
// import NotFound from '@/views/NotFound.vue';

export default {
    data() {
        return {
            fileStatusCode: 0,
            lastFolders: null,
            dirs: [],
            childName: null,
            currFolder: null,
            mouseOverRouterLink: "",
            isMetaKeyDown: false,
        }
    },
    props: {
        path: { type: [String, Array], required: false }
    },
    components: {
        DirectoryNavigation
    },
    computed: {
        folderRouteName(folder) {
            return this.dirs[folder]
        }
    },
    methods: {
        async checkKeyDown(event) {
            if (event.key === 'f') {
                if (this.mouseOverRouterLink != "") {
                    await fileOperate(this.mouseOverRouterLink, "openInFinder")
                }
            }
            else if (event.key === 'Meta') {
                this.isMetaKeyDown = true
            }
        },
        checkKeyUp(event) {
            if (event.key === 'Meta') {
                this.isMetaKeyDown = false
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
        async checkSignal() {
            if (this.$router.hasRoute(this.currFolder)) {
                await this.$router.push({ name: this.currFolder })
                return;
            }
            requestAnimationFrame(this.checkSignal);
        },

        async initData(currRouterName) {
            const url = config.server.concat(config.get.filemanager, "?path=", currRouterName)
            try {
                const response = await fetch(url)
                const resJson = await response.json()
                this.fileStatusCode = resJson["fileStatusCode"]
                this.lastFolders = resJson["fileList"]
                switch (this.fileStatusCode) {
                    case -1:
                        throw new Error(currRouterName + " not exists!");
                    case 0:
                        this.$router.addRoute(currRouterName,
                            {
                                path: "video-details",
                                name: currRouterName.concat("video-details"),
                                component: () => import('@/views/VideoDetails.vue'),
                                props: route => ({ ...route.params })
                            }
                        )
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
                return -1
            }
            for (var i = 0, len = this.lastFolders.length; i < len; ++i) {
                const childName = currRouterName.concat("/", this.lastFolders[i].filename)
                this.dirs[this.lastFolders[i].filename] = childName
                this.$router.addRoute(currRouterName,
                    {
                        path: this.lastFolders[i].filename,
                        name: childName,
                        component: () => import('@/components/DirectoryNavigation.vue'),
                        props: route => ({ ...route.params })
                    }
                )
            }
            return 0
        },
    },
    async created() {
        this.currFolder = "video"
        const res = await this.initData(this.currFolder)
        if (res != 0) {
            return
        }
        const currPath = this.path
        if (typeof (this.path) != 'undefined') {
            for (var i = 0, len = currPath.length; i < len; ++i) {
                this.currFolder = this.currFolder.concat('/', currPath[i])
                try {
                    await new Promise((resolve) => {
                        let timer = setInterval(() => {
                            if (this.$router.hasRoute(this.currFolder)) {
                                this.$router.push({ name: this.currFolder })
                                resolve(true)
                                clearInterval(timer)
                            }
                        }, 10)
                    })

                    if (typeof (res) != 'void') {
                        // window.location.href = '/NotFound'
                    }
                } catch (error) {
                    console.log('Request Failed:', error);
                    // window.location.href = '/NotFound'
                }
            }
        }
    }
}
</script>