import { createRouter, createWebHistory } from 'vue-router'
import HelloWorld from '../components/HelloWorld.vue'
import PlayView from '../views/PlayView.vue'
import DebugView from '../views/DebugView.vue'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'index',
      component: HomeView
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
    },
    {
      path: '/campaigns',
      name: 'campaigns',
      component: HelloWorld
    },
    {
      path: '/login',
      name: 'login',
      component: HelloWorld
    }
  ]
})

export default router
