<template>
    <el-affix>
        <el-anchor>
            <el-anchor-link href="#navigation" @click.prevent="scrollToTop">
                Directory
            </el-anchor-link>
            <el-anchor-link href="#introduction" @click.prevent="goToSectionByid('introduction')">
                Introduction
            </el-anchor-link>
            <el-anchor-link href="#previews" @click.prevent="goToSectionByid('previews')">
                Previews
            </el-anchor-link>
            <el-anchor-link href="#bookmarks" @click.prevent="goToSectionByid('bookmarks')">
                Bookmarks
            </el-anchor-link>
            <el-anchor-link href="#subtitles" @click.prevent="goToSectionByid('subtitles')">
                Subtitles
            </el-anchor-link>
            <el-anchor-link href="#statistics" @click.prevent="goToSectionByid('statistics')">
                Statistics
            </el-anchor-link>
        </el-anchor>
    </el-affix>
</template>

<script>
export default {
    methods: {
        scrollToTop() {
            window.scrollTo({ top: 0, left: 0, behavior: "smooth" })
        },
        goToSectionByid(id) {
            document.getElementById(id).scrollIntoView({ behavior: 'smooth', block: 'start', inline: 'nearest' })
        },
    }
}
</script>
