<template>
    <div class="gallery-cover">
        <router-link :to="{ name: this.getRouteName() }">
            <img @click="handleClick" @mouseover="this.isMouseOver = true" @mouseout="this.isMouseOver = false"
                :src="clipImgSrc()" :alt="clip.cover">
            <div class="cover-title">
                <p>{{ videoInfo.title }}</p>
            </div>
        </router-link>
    </div>
</template>

<script>
export default {
    data() {
        return {
            isMouseOver: false,
            clip: this.videoInfo.cover,
        }
    },

    props: {
        videoInfo: { type: Object, required: true },
        routePath: { type: String, required: true },
        webpPath: { type: String, required: true },
        // clip: { type: Object, required: true },
        isPlay: { type: Boolean, required: true },
    },

    methods: {
        getRouteName() {
            return this.routePath.slice(1, this.routePath.length)
        },
        async handleClick() {
            const routeName = this.getRouteName()
            await this.$router.push({ name: routeName })
        },
        getRealImagSrc(img) {
            return img.at(0) === '/' ? img : this.webpPath + "/" + img
        },
        clipImgSrc() {
            if (this.isPlay) {
                return this.getRealImagSrc(this.clip.webp)
            } else {
                return this.isMouseOver ? this.getRealImagSrc(this.clip.webp) : this.getRealImagSrc(this.clip.cover)
            }
        },
    }

}
</script>