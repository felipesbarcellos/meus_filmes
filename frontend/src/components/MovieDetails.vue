<template>
  <div class="container-fluid py-4 position-relative movie-detail-container" v-if="!loading && movie">
    <div class="backdrop-overlay" 
         :style="{ backgroundImage: movie.backdrop_path ? `url(https://image.tmdb.org/t/p/original${movie.backdrop_path})` : '' }">
    </div>

    <div class="container position-relative pt-5">
      <div class="row mt-5">
        <div class="col-md-4 mb-4 mb-md-0">
          <div class="poster-wrapper text-center">
            <img v-if="movie.poster_path" 
                 :src="getPosterUrl(movie.poster_path)" 
                 :alt="movie.title" 
                 class="img-fluid rounded shadow-lg poster-img" />
            <div v-else class="bg-dark poster-placeholder rounded d-flex align-items-center justify-content-center text-secondary">
              Sem Imagem
            </div>
          </div>
        </div>
        
        <div class="col-md-8">
          <div class="card bg-dark text-light">
            <div class="card-body p-4">
              <h1 class="display-5 text-primary mb-1">{{ movie.title }}</h1>
              <p class="lead fst-italic text-light-emphasis mb-3" v-if="movie.tagline">{{ movie.tagline }}</p>
              
              <div class="d-flex flex-wrap gap-3 mb-3 text-secondary">
                <span>{{ movie.release_date ? movie.release_date.substring(0, 4) : 'N/A' }}</span>
                <span class="text-secondary">|</span>
                <span>{{ formatRuntime(movie.runtime) }}</span>
                <span class="text-secondary">|</span>
                <span>Diretor: {{ getDirector(movie.credits) }}</span>
              </div>
              
              <div class="mb-4">
                <span v-for="genre in movie.genres" :key="genre.id" 
                      class="badge bg-primary bg-opacity-75 me-2 mb-2 py-2 px-3 rounded-pill">
                  {{ genre.name }}
                </span>
              </div>
              
              <h5 class="border-bottom border-primary pb-2 mb-3">Sinopse</h5>
              <p class="text-light-emphasis">{{ movie.overview || "Sinopse não disponível." }}</p>

              <!-- Actions Section -->
              <div class="mt-4 d-flex flex-wrap gap-3" v-if="authStore.isAuthenticated">
                <button @click="showListModal = true" class="btn btn-primary">
                  <i class="bi bi-plus-circle me-1"></i> Adicionar à Lista
                </button>
                
                <div class="d-flex flex-wrap gap-2 align-items-center">
                  <input type="date" v-model="watchedDate" class="form-control bg-dark text-light border-secondary"/>
                  <button @click="handleMarkAsWatched" class="btn btn-success">
                    <i class="bi bi-check-circle me-1"></i> Marcar como Assistido
                  </button>
                </div>
              </div>
              
              <div class="mt-3">
                <div v-if="watchedSuccess" class="alert alert-success py-2 px-3">{{ watchedSuccess }}</div>
                <div v-if="watchedError" class="alert alert-danger py-2 px-3">{{ watchedError }}</div>
              </div>
              
              <!-- Trailer Section -->
              <div v-if="getTrailerKey(movie.videos)" class="mt-5">
                <h5 class="border-bottom border-primary pb-2 mb-3">Trailer</h5>
                <div class="ratio ratio-16x9">
                  <iframe 
                    :src="`https://www.youtube.com/embed/${getTrailerKey(movie.videos)}`" 
                    allowfullscreen
                    class="rounded shadow-sm"
                  ></iframe>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <div v-if="loading" class="d-flex justify-content-center align-items-center py-5 my-5">
    <div class="spinner-border text-primary me-3" role="status">
      <span class="visually-hidden">Carregando...</span>
    </div>
    <p class="h5 text-secondary">Carregando detalhes do filme...</p>
  </div>
  
  <div v-if="error && !loading" class="alert alert-danger mx-auto my-5 text-center" style="max-width: 500px;">
    {{ error }}
  </div>

  <!-- Modal para Adicionar à Lista -->
  <div v-if="showListModal" class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.7);">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content bg-dark text-light">
        <div class="modal-header border-secondary">
          <h5 class="modal-title">Adicionar "{{ movie.title }}" à lista:</h5>
          <button type="button" class="btn-close btn-close-white" aria-label="Close" @click="showListModal = false"></button>
        </div>
        <div class="modal-body">
          <div v-if="userLists.length > 0">
            <select v-model="selectedListId" class="form-select bg-dark text-light border-secondary mb-3">
              <option v-for="list in userLists" :key="list.id" :value="list.id">{{ list.name }}</option>
            </select>
            <button @click="handleAddToList" class="btn btn-primary w-100">Confirmar</button>
          </div>
          <p v-else class="text-center text-secondary">Você não possui listas. Crie uma primeiro!</p>
          <div v-if="addToListSuccess" class="alert alert-success mt-3">{{ addToListSuccess }}</div>
          <div v-if="addToListError" class="alert alert-danger mt-3">{{ addToListError }}</div>
        </div>
        <div class="modal-footer border-secondary">
          <button @click="showListModal = false" class="btn btn-secondary">Fechar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth' // Já importado
import { apiGet, apiPost } from '@/utils/api' // Importar funções da API

const API_BASE_URL = '/api/tmdb'
const BACKEND_API_URL = '/api'

const route = useRoute()
const authStore = useAuthStore() // Instância do store já criada

// ... existing refs ...
const movie = ref(null)
const loading = ref(true)
const error = ref(false)
const showListModal = ref(false)
const userLists = ref([])
const selectedListId = ref(null)
const addToListSuccess = ref('')
const addToListError = ref('')
const watchedSuccess = ref('')
const watchedError = ref('')
const watchedDate = ref(new Date().toISOString().split('T')[0])

const fetchMovie = async () => {
  loading.value = true
  error.value = false
  try {
    // Usa apiGet e já recebe o JSON
    const data = await apiGet(`${API_BASE_URL}/movie/${route.params.id}?append_to_response=credits,videos`)
    movie.value = data
  } catch (e) {
    error.value = e.message || "Erro ao buscar detalhes do filme."
    console.error("Erro ao buscar detalhes do filme:", e)
  } finally {
    loading.value = false
  }
}

const fetchUserLists = async () => {
  if (!authStore.isAuthenticated || !authStore.user?.id) return
  try {
    // Usa apiGet e já recebe o JSON
    const data = await apiGet(`${BACKEND_API_URL}/lists/`)
    userLists.value = data
    if (userLists.value.length > 0) {
      selectedListId.value = userLists.value[0].id
    }
  } catch (e) {
    console.error(e.message)
    addToListError.value = e.message
  }
}

const handleAddToList = async () => {
  if (!selectedListId.value || !movie.value || !authStore.isAuthenticated || !authStore.user?.id) return
  addToListSuccess.value = ''
  addToListError.value = ''
  try {
    // Usa apiPost e já recebe o JSON
    const data = await apiPost(`${BACKEND_API_URL}/lists/add_movie`, {
      list_id: selectedListId.value,
      tmdb_id: movie.value.id,
    })
    addToListSuccess.value = data.msg || 'Filme adicionado com sucesso!'
    setTimeout(() => { showListModal.value = false; addToListSuccess.value = ''; }, 2000)
  } catch (e) {
    console.error(e.message)
    addToListError.value = e.message
  }
}

const handleMarkAsWatched = async () => {
  if (!movie.value || !authStore.isAuthenticated || !authStore.user?.id) return
  watchedSuccess.value = ''
  watchedError.value = ''
  try {
    // Usa apiPost e já recebe o JSON
    const data = await apiPost(`${BACKEND_API_URL}/movie/watched/`, {
      tmdb_id: movie.value.id,
      watched_at: watchedDate.value
    })
    watchedSuccess.value = data.msg || 'Filme marcado como assistido!'
    setTimeout(() => { watchedSuccess.value = ''; }, 3000)
  } catch (e) {
    console.error(e.message)
    watchedError.value = e.message
  }
}

function getPosterUrl(path) {
  return path ? `https://image.tmdb.org/t/p/w500${path}` : '' // Fallback para string vazia se não houver path
}

function formatRuntime(minutes) {
  if (!minutes) return ''
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return `${h}h ${m}min`
}

function getDirector(credits) {
  if (!credits || !credits.crew) return 'N/A'
  const director = credits.crew.find(person => person.job === 'Director')
  return director ? director.name : 'N/A'
}

function getTrailerKey(videos) {
  if (!videos || !videos.results) return null
  const trailer = videos.results.find(video => video.type === 'Trailer' && video.site === 'YouTube')
  return trailer ? trailer.key : null
}

onMounted(() => {
  fetchMovie()
  // fetchUserLists será chamado pelo watch em authStore.isAuthenticated
  // ou se já estiver autenticado no momento do mount
  if (authStore.isAuthenticated) {
    fetchUserLists()
  }
})

watch(() => route.params.id, () => {
  fetchMovie()
  addToListSuccess.value = ''
  addToListError.value = ''
  watchedSuccess.value = ''
  watchedError.value = ''
  showListModal.value = false
  // Não precisa recarregar as listas do usuário aqui, elas não mudam com o filme
})

// Observa o estado de autenticação para buscar/limpar listas do usuário
watch(() => authStore.isAuthenticated, (newIsAuthenticated) => {
  if (newIsAuthenticated) {
    fetchUserLists() // Busca listas quando o usuário faz login
  } else {
    userLists.value = [] // Limpa listas quando o usuário faz logout
    selectedListId.value = null
    showListModal.value = false // Fecha o modal se estiver aberto
  }
}, { immediate: true }) // `immediate: true` para rodar na montagem inicial se já autenticado

</script>

<style scoped>
/* Custom styles to complement Bootstrap */
.backdrop-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 60vh;
  background-size: cover;
  background-position: center center;
  filter: brightness(0.4) blur(3px);
  z-index: 0;
}

.movie-detail-container {
  min-height: 90vh;
}

.poster-wrapper {
  position: relative;
  z-index: 1;
}

.poster-img {
  transition: transform 0.3s ease;
  max-height: 500px;
  object-fit: cover;
}

.poster-img:hover {
  transform: scale(1.03);
}

.poster-placeholder {
  width: 100%;
  height: 375px;
  font-size: 1.2rem;
}

/* Bootstrap Modal backdrop blur */
.modal {
  backdrop-filter: blur(5px);
}

/* Gap utility (if not using Bootstrap 5.2+) */
.gap-2 {
  gap: 0.5rem;
}

.gap-3 {
  gap: 1rem;
}

/* Make the container position relative to contain backdrop */
.container {
  z-index: 1;
}
</style>
