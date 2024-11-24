<template>
    <div id="navigation">
        <a id="logo" href="/video/All">
            <Logo />
        </a>
        <router-link :to="{ name: 'video' }">Video</router-link>
        <a href="" @click.prevent=" shutdownDialogVisible = true">Backend</a>
        <a href="https://github.com/MouJieQin/varchive" target="_blank">Github</a>
        <a href="https://github.com/MouJieQin/varchive/releases" target="_blank">Update</a>
    </div>
    <Backend :dialogVisible="shutdownDialogVisible" :setDialogVisible="(val) => { this.shutdownDialogVisible = val }" />
</template>

<script>
import Logo from '@/components/Logo.vue'
import Backend from '@/components/Backend.vue'


export default {
    data() {
        return {
            shutdownDialogVisible: false,
        }
    },
    components: { Logo, Backend },
    methods: {
    }
}
</script>
