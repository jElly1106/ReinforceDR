import { createRouter, createWebHistory } from "vue-router";


const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "login",
      component: () => import("../views/Login/LoginAndRegisterView.vue"),
    },
    {
      path: "/sum",
      name: "sum",
      component: () => import("../views/SumView.vue"),
      children:[
        {
          path: "home",
          name: "home",
          component: () => import("../views/Home/HomeView.vue"),  
        },
        {
          path: "modelpredict",
          name: "modelpredict",
          component: () => import("../views/Model/ModelPredictView.vue"),  
        },        
        {
          path: "history",
          name: "history",
          component: () => import("../views/Model/ModelPredictHistoryView.vue"),
        },
        {
          path: "segmentationResult/:id",
          name: "segmentationResult",
          component: () => import("../views/Model/HistoryDetail.vue"),
          props: true // 可选：将params自动转为props
        },
        {
          path: "testTable",
          name: "testTable",
          component: () => import("../components/TrainRecordTable.vue"),  
        },
        {
            path: "ai",
            name: "ai",
            component: () => import("../views/AiView/AiView.vue"),  
        },
        { 
            path: "ai/chat",
            name: "ai-chat",
            component: () => import("../views/AiView/ChatPage.vue"),  
        }
      ]
    },
    {
      path: "/admin",
      name: "admin",
      component: () => import("../views/Admin/AdminView.vue"),
    },
    {
      path:"/load",
      name:"load",
      component: () => import("../components/LoadComponent.vue"),
    }
  ],
});

export default router
