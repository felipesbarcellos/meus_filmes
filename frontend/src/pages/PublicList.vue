<template>
  <div class="container py-4">
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">{{ $t('general.loading') }}</span>
      </div>
      <p class="mt-3 text-secondary">{{ $t('publicList.loadingMessage') }}</p>
    </div>
    <div v-else-if="error" class="alert alert-danger text-center" role="alert">
      {{ error }} <!-- API error messages might need specific handling or generic keys -->
    </div>
    <div v-else>
      <h2 class="mb-3">{{ list.name }}</h2>
      <div class="d-flex align-items-center gap-3 mb-4">
        <span v-if="list.is_main" class="badge bg-primary">{{ $t('publicList.mainListBadge') }}</span>
        <span class="text-secondary small">{{ $t('publicList.listIdPrefix') }}{{ list.id }}</span>
      </div>
      <div v-if="moviesData.length === 0" class="alert alert-secondary text-center">
        {{ $t('publicList.noMoviesInList') }}
      </div>
      <MovieList v-else :movies="moviesData" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import MovieList from '@/components/MovieList.vue'
import { apiGet } from '@/utils/api'
import { useI18n } from 'vue-i18n' // Import useI18n

const { t, locale } = useI18n() // Initialize t and locale

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
      const lang = locale.value === 'en' ? 'en-US' : 'pt-BR'
      const promises = data.movies.map(async (movieItem) => {
        let idForApiCall = typeof movieItem === 'object' && movieItem !== null ? movieItem.tmdb_id : movieItem
        if (!idForApiCall) return null
        try {
          const movieDetails = await apiGet(`${API_BASE_URL}/movie/${idForApiCall}?language=${lang}`)
          return movieDetails
        } catch (e) {
          // Log individual movie fetch error, but don't necessarily fail the whole page
          console.error(`Error fetching details for movie ${idForApiCall}:`, e)
          return null
        }
      })
      moviesData.value = (await Promise.all(promises)).filter(Boolean)
    } else {
      moviesData.value = []
    }
  } catch (e) {
    error.value = e.message || t('publicList.fetchError')
    list.value = { id: null, name: '', is_main: false, user_id: null, movies: [] }
    moviesData.value = []
  } finally {
    loading.value = false
  }
}

onMounted(fetchPublicListDetails)

watch(locale, () => {
  fetchPublicListDetails()
})
</script>

<style scoped>
.gap-3 {
  gap: 1rem;
}
</style>
