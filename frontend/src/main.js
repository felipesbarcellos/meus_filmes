import { createApp } from 'vue'
import { createPinia } from 'pinia' // Importar createPinia
import App from './App.vue'
import { createRouter, createWebHistory } from 'vue-router'
import Home from './pages/Home.vue'
import MovieDetails from './components/MovieDetails.vue'
import GenreMovies from './pages/GenreMovies.vue'
import Register from './pages/Register.vue'
import Login from './pages/Login.vue'
import Buscar from './pages/Buscar.vue'
import MovieLists from './components/MovieLists.vue'
import ListDetails from './components/ListDetails.vue'
import WatchedList from './components/WatchedList.vue'
import PopularMoviesPage from './pages/PopularMoviesPage.vue'
import { useAuthStore } from './stores/auth' // Importar o store de autenticação
import { setupApi } from './utils/api' // Importar configuração de API
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap' // Imports Bootstrap's JavaScript (which includes Popper.js if bundled)
import './style.css' // Import custom styles AFTER Bootstrap so they override Bootstrap defaults

const routes = [
  { path: '/', component: Home },
  { path: '/buscar', component: Buscar },
  { path: '/movie/:id', component: MovieDetails, props: true },
  { path: '/genre/:id', component: GenreMovies, props: true },
  { path: '/registrar', component: Register },
  { path: '/login', component: Login },
  {
    path: '/minhas-listas',
    component: MovieLists,
    meta: { requiresAuth: true } // Adiciona meta para indicar rota protegida
  },
  {
    path: '/listas',
    component: MovieLists,
    meta: { requiresAuth: true } // Adiciona meta para indicar rota protegida
  },
  {
    path: '/listas/:id',
    component: ListDetails,
    meta: { requiresAuth: true } // Adiciona meta para indicar rota protegida
  },
  {
    path: '/assistidos',
    component: WatchedList,
    meta: { requiresAuth: true } // Adiciona meta para indicar rota protegida
  },
  {
    path: '/popular-movies',
    component: PopularMoviesPage // Assign the new component here
  },
  {
    path: '/listas/publica/:id',
    component: () => import('./pages/PublicList.vue'),
    // Public, no auth required
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // always scroll to top
    return { top: 0 }
  }
})

// Guarda de navegação global
router.beforeEach((to, from, next) => {
  // É crucial inicializar o store Pinia ANTES de usá-lo no beforeEach.
  // No entanto, o store já é inicializado quando o app é criado e `app.use(pinia)` é chamado.
  // Para acessar o store aqui, precisamos garantir que ele esteja disponível.
  // Uma forma é importá-lo diretamente, pois ele é um singleton após a inicialização.
  const authStore = useAuthStore()

  // Verifica se a rota requer autenticação e se o usuário não está logado
  if (to.matched.some(record => record.meta.requiresAuth) && !authStore.isAuthenticated) {
    // Redireciona para a página de login
    next({ path: '/login', query: { redirect: to.fullPath } }) // Guarda a rota original para redirecionamento após login
  } else {
    next() // Prossegue para a rota
  }
})

const app = createApp(App)

app.use(createPinia()) // Usar Pinia - Certifique-se que isso acontece antes de router.beforeEach ser efetivamente usado na navegação inicial.
app.use(router)

// Configurar utilitário de API com o router
setupApi(router)

app.mount('#app')


