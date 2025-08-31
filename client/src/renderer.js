import { createApp } from 'vue'
import App from './App.vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import 'chota/dist/chota.min.css'
import './index.css'
import VueApexCharts from 'vue3-apexcharts'

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

const app = createApp(App)

app.use(pinia)
app.use(VueApexCharts)
app.mount('#app')
