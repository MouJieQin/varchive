<template>
    <div class="image-container">
        <img class="cover" @mouseover="isMouseOver = true" @mouseout="isMouseOver = false" :src="clipImgSrc()"
            :alt="clip.cover">
        <div v-show="!isMouseOver" class="image-timestamp">{{ formatTime(clip.startTime) }}</div>
    </div>
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
        formatTime(totalSeconds) {
            const hours = Math.floor(totalSeconds / 3600);
            const minutes = Math.floor((totalSeconds % 3600) / 60);
            const seconds = Math.floor(totalSeconds % 60);

            const formattedHours = String(hours).padStart(2, '0');
            const formattedMinutes = String(minutes).padStart(2, '0');
            const formattedSeconds = String(seconds).padStart(2, '0');

            return `${formattedHours}:${formattedMinutes}:${formattedSeconds}`;
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