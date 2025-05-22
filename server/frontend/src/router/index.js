import { createRouter, createWebHistory } from 'vue-router'
import HelloWorld from '../components/HelloWorld.vue'
import PlayView from '../views/PlayView.vue'
import DebugView from '../views/DebugView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'index',
      component: HelloWorld
    },
    {
      path: '/play',
      name: 'play',
      component: PlayView
    },
    {
      path: '/debug',
      name: 'debug',
      component: DebugView
    }
  ],
})

export default router
