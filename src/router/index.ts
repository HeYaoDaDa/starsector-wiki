import { route } from 'quasar/wrappers';
import {
  createMemoryHistory,
  createRouter,
  createWebHashHistory,
  createWebHistory,
} from 'vue-router';

import routes from './routes';
import { appData } from 'src/AppData';

/*
 * If not building with SSR mode, you can
 * directly export the Router instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Router instance.
 */

export default route(function (/* { store, ssrContext } */) {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : process.env.VUE_ROUTER_MODE === 'history'
    ? createWebHistory
    : createWebHashHistory;

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,

    // Leave this as is and make changes in quasar.conf.js instead!
    // quasar.conf.js -> build -> vueRouterMode
    // quasar.conf.js -> build -> publicPath
    history: createHistory(process.env.VUE_ROUTER_BASE),
  });

  Router.beforeEach(async (to) => {
    if (to.meta.requireGameData) {
      if (['none', 'loading'].includes(appData.status.value)) {
        sessionStorage.setItem('redirectAfterLoad', to.fullPath);
        return '/load';
      }
      if (!appData.selectedVersion.value) {
        return '/load';
      }
      // Persist current selections on navigation
      localStorage.setItem('selectedVersion', appData.selectedVersion.value);
      localStorage.setItem('locale', appData.selectedLocale.value);
      // Clear redirect cache on normal navigation after data is loaded
      sessionStorage.removeItem('redirectAfterLoad');
    }
  });

  return Router;
});
