import { createRouter, createWebHashHistory } from 'vue-router'
import homePage from '@/views/homePage.vue'
import loginPage from '@/views/loginPage.vue'

const router=createRouter({
    history:createWebHashHistory(),
    routes:[
        {
            path:'/',
            component:loginPage,
        },
        {
            path:'/home',
            component:homePage,
        },
        {
            path:'/login',
            component:loginPage,
        },
    ]
})

export default router