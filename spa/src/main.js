import '@/main.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import 'element-plus/dist/index.css'

import App from '@/App.vue'
import router from '@/router'
import ElementPlus from 'element-plus'
import {createApp} from 'vue'

const app = createApp(App)
app.use(router).use(ElementPlus).mount('#app')
