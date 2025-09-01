import { createApp } from 'vue'
import { createPinia } from 'pinia'
import 'vue3-toastify/dist/index.css'
import Vue3Toastify, { toast } from 'vue3-toastify'
import './style.css'
import App from './App.vue'
import router from './router'

createApp(App).use(router).use(createPinia()).use(Vue3Toastify, {
  autoClose: 5000,
  position: toast.POSITION.TOP_CENTER,
  pauseOnHover: true
}).mount('#app')
