<template>
  <div class="container py-4">
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Carregando...</span>
      </div>
      <p class="mt-3 text-secondary">Carregando lista pública...</p>
    </div>
    <div v-else-if="error" class="alert alert-danger text-center" role="alert">
      {{ error }}
    </div>
    <div v-else>
      <h2 class="mb-3">{{ list.name }}</h2>
      <div class="d-flex align-items-center gap-3 mb-4">
        <span v-if="list.is_main" class="badge bg-primary">Principal</span>
        <span class="text-secondary small">ID: {{ list.id }}</span>
      </div>
      <div v-if="moviesData.length === 0" class="alert alert-secondary text-center">
        Nenhum filme nesta lista ainda.
      </div>
      <MovieList v-else :movies="moviesData" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import MovieList from '@/components/MovieList.vue'
import { apiGet } from '@/utils/api'

const route = useRoute()
const list = ref({ id: null, name: '', is_main: false, user_id: null, movies: [] })
const loading = ref(true)
const error = ref('')
const moviesData = ref([])
const API_BASE_URL = '/api/tmdb'
const BACKEND_API_URL = '/api'

async function fetchPublicListDetails() {
  loading.value = true
  error.value = ''
  try {
    const data = await apiGet(`${BACKEND_API_URL}/lists/public/${route.params.id}`)
    list.value = data
    if (data.movies && data.movies.length > 0) {
      const promises = data.movies.map(async (movieItem) => {
        let idForApiCall = typeof movieItem === 'object' && movieItem !== null ? movieItem.tmdb_id : movieItem
        if (!idForApiCall) return null
        try {
          const movieDetails = await apiGet(`${API_BASE_URL}/movie/${idForApiCall}`)
          return movieDetails
        } catch (e) {
          return null
        }
      })
      moviesData.value = (await Promise.all(promises)).filter(Boolean)
    } else {
      moviesData.value = []
    }
  } catch (e) {
    error.value = e.message || 'Erro ao buscar lista pública.'
    list.value = { id: null, name: '', is_main: false, user_id: null, movies: [] }
    moviesData.value = []
  } finally {
    loading.value = false
  }
}

onMounted(fetchPublicListDetails)
</script>

<style scoped>
.gap-3 {
  gap: 1rem;
}
</style>
