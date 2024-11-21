<template>
    <div id="navigation">
        <router-link id="logo" :to="{ name: 'video' }">
            <Logo />
        </router-link>
        <router-link :to="{ name: 'video' }">Video</router-link>
        <router-link>
            <p @click.prevent="shutdownDialogVisible = true">Exit</p>
        </router-link>
        <!-- <router-link :to="{ name: 'help' }">Help</router-link> -->
    </div>
    <!-- <Shutdown  /> -->
    <Shutdown :dialogVisible="shutdownDialogVisible" :setDialogVisible="(val) => { this.shutdownDialogVisible = val }" />
</template>

<script>
import Logo from '@/components/Logo.vue'
import Shutdown from '@/components/Shutdown.vue'


export default {
    data() {
        return {
            shutdownDialogVisible: false,
        }
    },
    components: { Logo, Shutdown },
    methods: {
    }
}
</script>
