import {createRouter, createWebHistory} from 'vue-router'


const routes =
    [
      {
        path: '/video/:path+',
        name: 'videop',
        component: () => import('@/views/Video.vue'),
        props: route => ({...route.params})
      },
      {
        path: '/video',
        name: 'video',
        component: () => import('@/views/Video.vue'),
        // props: route => ({...route.params}),
      },
      {
        path: '/help',
        name: 'help',
        component: () => import('@/views/Help.vue')
      },
      {
        path: '/:pathMatch(.*)*',
        name: 'NotFound',
        component: () => import('@/views/NotFound.vue')
      }
    ]

    const router = createRouter({
      history: createWebHistory(),
      routes,
      linkActiveClass: 'varchive-video-active-link'
    })

export default router
