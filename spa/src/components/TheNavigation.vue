<template>
    <div id="navigation">
        <router-link id="logo" :to="{ name: 'video' }">
            <Logo />
        </router-link>
        <router-link :to="{ name: 'video' }">Video</router-link>
        <router-link>
            <p @click.prevent="shutdownDialogVisible = true">Backend</p>
        </router-link>
        <!-- <router-link :to="{ name: 'help' }">Help</router-link> -->
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
