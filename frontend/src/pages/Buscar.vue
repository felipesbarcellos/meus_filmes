<template>
  <div class="container py-4">
    <form @submit.prevent="triggerSearchNow" class="row mb-4 p-4 bg-dark rounded shadow">
      <div class="col-md-10 mb-2 mb-md-0">
        <input type="text" v-model="query" placeholder="Buscar por filmes..." class="form-control form-control-lg bg-dark text-light border-secondary" />
      </div>
      <div class="col-md-2">
        <button type="submit" class="btn btn-primary w-100 py-2" :disabled="loading">
          {{ loading ? 'Buscando...' : 'Buscar' }}
        </button>
      </div>
    </form>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Carregando...</span>
      </div>
      <p class="mt-3 text-secondary">Carregando resultados...</p>
    </div>
    
    <div v-if="error && !loading" class="alert alert-danger" role="alert">
      {{ error }}
    </div>

    <div v-if="!loading && searched && results.length === 0 && !error && queryWhenSearched" class="text-center py-5 text-secondary">
      Nenhum filme encontrado para "{{ queryWhenSearched }}". Tente um termo diferente.
    </div>

    <div v-if="results.length > 0 && !loading" class="row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4 row-cols-xl-5 g-4">
      <div v-for="movie in results" :key="movie.id" class="col">
        <div class="card h-100 bg-dark text-light border-secondary movie-card" @click="goToMovie(movie.id)">
          <div class="poster-container bg-dark">
            <img :src="getPosterUrl(movie.poster_path)" :alt="movie.title" class="card-img-top movie-poster" v-if="movie.poster_path" />
            <div v-else class="d-flex justify-content-center align-items-center h-100 text-secondary">
              Sem Imagem
            </div>
          </div>
          <div class="card-body">
            <h5 class="card-title">{{ movie.title }}</h5>
            <p class="card-text small text-secondary" v-if="movie.release_date">
              Lançamento: {{ movie.release_date.substring(0, 4) }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue' // Importar watch
import { useRouter } from 'vue-router'
import { apiGet } from '@/utils/api'

const API_BASE_URL = '/api/tmdb'

const query = ref('')
const results = ref([])
const loading = ref(false)
const error = ref(false)
const searched = ref(false)
const queryWhenSearched = ref('') // Para guardar o termo buscado para a mensagem "Nenhum filme encontrado"
const router = useRouter()

let debounceTimer = null

// Função de busca principal
async function performSearch(searchTerm) {
  if (!searchTerm.trim()) {
    results.value = []
    searched.value = true
    queryWhenSearched.value = searchTerm // Atualiza mesmo se vazio para limpar a mensagem anterior
    error.value = false
    return
  }
  loading.value = true
  error.value = false
  // Não limpar results.value aqui para uma UX mais suave enquanto digita
  // results.value = [] 
  try {
    const data = await apiGet(`${API_BASE_URL}/search?query=${encodeURIComponent(searchTerm)}`)
    results.value = data.results || []
    searched.value = true
    queryWhenSearched.value = searchTerm // Guarda o termo que foi efetivamente buscado
  } catch (e) {
    error.value = e.message || "Erro ao buscar filmes."
    console.error("Erro ao buscar filmes:", e)
    results.value = []
  } finally {
    loading.value = false
  }
}

// Observa a variável query
watch(query, (newQuery) => {
  clearTimeout(debounceTimer)
  if (newQuery.trim() === '') {
    results.value = [] // Limpa resultados imediatamente se o campo estiver vazio
    searched.value = false // Reseta o estado de "buscado"
    queryWhenSearched.value = ''
    return
  }
  debounceTimer = setTimeout(() => {
    performSearch(newQuery)
  }, 500) // Espera 500ms após o usuário parar de digitar
})

// Função para o botão de busca (caso o usuário clique antes do debounce)
function triggerSearchNow() {
  clearTimeout(debounceTimer) // Cancela qualquer busca pendente do debounce
  performSearch(query.value)
}

function getPosterUrl(path) {
  return path ? `https://image.tmdb.org/t/p/w300${path}` : ''
}

function goToMovie(id) {
  router.push(`/movie/${id}`)
}
</script>

<style scoped>
/* Minimalist custom styles to complement Bootstrap */
.movie-card {
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.movie-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 20px rgba(var(--bs-primary-rgb), 0.3);
}

.poster-container {
  aspect-ratio: 2 / 3;
}

.movie-poster {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Mobile responsiveness is handled by Bootstrap's responsive classes */
</style>
