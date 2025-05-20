<template>
  <div class="container py-4">
    <form @submit.prevent="handleSearch" class="row mb-4 p-4 bg-dark rounded shadow">
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

    <div v-if="!loading && searched && results.length === 0 && !error" class="text-center py-5 text-secondary">
      Nenhum filme encontrado para "{{ query }}". Tente um termo diferente.
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { apiGet } from '@/utils/api'

const API_BASE_URL = '/api/tmdb' // URL base do seu backend para TMDB

const query = ref('')
const results = ref([])
const loading = ref(false)
const error = ref(false)
const searched = ref(false) // Para saber se uma busca já foi feita
const router = useRouter()

async function handleSearch() {
  if (!query.value.trim()) {
    results.value = []
    searched.value = true // Considera como "buscado" para mostrar mensagem de "nada encontrado"
    error.value = false
    return
  }
  loading.value = true
  error.value = false
  searched.value = false
  results.value = []
  try {
    // Usa apiGet para centralizar tratamento de erro, se desejar
    const data = await apiGet(`${API_BASE_URL}/search?query=${encodeURIComponent(query.value)}`)
    results.value = data.results || []
    searched.value = true
  } catch (e) {
    error.value = e.message || "Erro ao buscar filmes."
    console.error("Erro ao buscar filmes:", e)
    results.value = [] // Limpa resultados em caso de erro
  } finally {
    loading.value = false
  }
}

function getPosterUrl(path) {
  return path ? `https://image.tmdb.org/t/p/w300${path}` : '' // Fallback para string vazia
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
