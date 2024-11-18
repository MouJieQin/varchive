<template>
    <div v-if="isShow">
        <section class="container">
            <h1>{{ this.$route.name }}</h1>

            <div v-for="video in varchiveVideos" :key="video">
                {{ video }}
            </div>
        </section>
    </div>
</template>

<script>
export default {
    data() {
        return {
            varchiveVideos: []
        }
    },
    props: {
        routeName: { type: String, Required: true },
        fileStatusCode: { type: Number, Required: true },
        folders: { type: Array, Required: true }
    },
    computed: {
        isShow() {
            return this.routeName === this.$route.name && this.fileStatusCode === 2
        }
    },
    methods: {
        initData() {
            if (this.fileStatusCode === 2) {
                const varchiveFolders = this.folders.filter((ele) => {
                    return ele.type === "varchive-video"
                })
                for (var i = 0, len = varchiveFolders.length; i < len; ++i) {
                    this.varchiveVideos.push(this.routeName.concat(varchiveFolders[i].filename))
                }
            }
        }
    },

    async created() {
        this.initData()
    }
}
</script>