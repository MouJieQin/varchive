<template>
    <div>
        <div v-html="markdown.render(data)"></div>
    </div>
</template>

<script>
import MarkdownIt from 'markdown-it'

export default {
    data() {
        return {
            data: '# There should be the help docments for Varchive',
            markdown: new MarkdownIt()
        }
    },
}
</script>