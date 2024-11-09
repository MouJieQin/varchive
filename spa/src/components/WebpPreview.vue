<template>
    <img class="cover" @mouseover="this.isMouseOver = true" @mouseout="this.isMouseOver = false" :src="clipImgSrc()"
        :alt="clip.cover">
</template>

<script>
export default {
    data() {
        return {
            isMouseOver: false,
        }
    },

    props: {
        webpPath: { type: String, required: true },
        clip: { type: Object, required: true },
        isPlay: { type: Boolean, required: true },
    },


    methods: {
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