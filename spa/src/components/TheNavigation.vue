<template>
    <div id="navigation">
        <router-link id="logo" :to="{ name: 'video' }">
            <Logo />
        </router-link>
        <router-link :to="{ name: 'video' }">Video</router-link>
        <!-- <router-link :to="{ name: 'help' }">Help</router-link> -->
    </div>
</template>

<script>
import Logo from '@/components/Logo.vue'
export default {
    data() {
        return {

        }
    },
    components: { Logo },
}
</script>
