import { createApp } from 'vue';
import { registerPlugins } from '@/plugins';
import App from './App.vue';
import router from './router';
import 'unfonts.css';

const app = createApp(App);
registerPlugins(app);

if (import.meta.hot) {
   import.meta.hot.on('vite:beforeFullReload', () => {
      throw '(skipping full reload)';
   });
}

app.use(router);
app.mount('#app');
