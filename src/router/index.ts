import { createRouter, createWebHistory } from 'vue-router';
import QuizView from '@/views/QuizView.vue';

const routes = [
  {
    path: "/",
    redirect: "/quiz"
  },
  {
    path: "/quiz",
    component: QuizView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;