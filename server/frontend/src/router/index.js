import { createRouter, createWebHistory } from 'vue-router'
import HelloWorld from '../components/HelloWorld.vue'
import CombatGrid from '../components/CombatGrid.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'index',
      component: HelloWorld,
    },
    {
      path: '/grid',
      name: 'grid',
      component: CombatGrid,
    }
  ],
})

export default router
