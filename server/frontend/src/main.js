import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import VueCookies from 'vue-cookies'
import vue3GoogleLogin from 'vue3-google-login'
import router from './router'

const app = createApp(App)

app.use(VueCookies);
app.use(vue3GoogleLogin, {
    clientId: '287550445029-b1qa6m8565d6eeu1tm7hvmr53j6m9ciu.apps.googleusercontent.com',
    clientSecret: import.meta.env.VITE_GOOGLE_CLIENT_SECRET
})
app.use(router)

app.mount('#app')
