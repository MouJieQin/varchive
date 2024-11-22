<template>
    <div id="navigation">
        <router-link id="logo" :to="{ name: 'video' }">
            <Logo />
        </router-link>
        <router-link :to="{ name: 'video' }">Video</router-link>
        <a @click.prevent=" shutdownDialogVisible = true">Backend</a>
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
