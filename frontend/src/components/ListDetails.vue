<template>
  <div class="container py-4">
    <div class="card bg-dark text-light shadow mb-4">
      <div class="card-body p-4">
        <div v-if="loading" class="text-center py-4">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">{{ $t('listDetails.loading.srOnly') }}</span>
          </div>
          <p class="mt-3 text-secondary">{{ $t('listDetails.loading.text') }}</p>
        </div>
        
        <div v-else-if="error" class="alert alert-danger" role="alert">
          {{ error }}
        </div>
        
        <div v-else>
          <h2 class="mb-3">{{ list.name }}</h2>
          <div class="d-flex align-items-center gap-3 mb-4">
            <span v-if="list.is_main" class="badge bg-primary">{{ $t('listDetails.mainBadge') }}</span>
            <span class="text-secondary small">{{ $t('listDetails.idLabel') }} {{ list.id }}</span>
          </div>
          
          <div v-if="moviesData.length === 0" class="alert alert-secondary text-center">
            {{ $t('listDetails.noMovies') }}
          </div>
          <div class="d-flex justify-content-end mb-3" v-if="list.id">
            <button class="btn btn-outline-primary btn-sm" @click="shareListLink">
              <i class="bi bi-share"></i> {{ $t('listDetails.shareListButton') }}
            </button>
          </div>
          <MovieList v-if="moviesData.length > 0" :movies="moviesData" :showRemoveFromList="true" @remove-from-list="handleRemoveFromList" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n' // Import useI18n
import MovieList from './MovieList.vue'
import { useAuthStore } from '@/stores/auth'
import { apiGet, apiDelete } from '@/utils/api'

const { t } = useI18n() // Initialize t
const route = useRoute()
const authStore = useAuthStore()

const list = ref({ id: null, name: '', is_main: false, user_id: null, movies: [] })
const loading = ref(true)
const error = ref('')
const moviesData = ref([])

const API_BASE_URL = '/api/tmdb'
const BACKEND_API_URL = '/api'

async function fetchListDetails() {
  if (!authStore.isAuthenticated) {
    error.value = t('listDetails.error.authRequired')
    loading.value = false
    list.value = { id: null, name: '', is_main: false, user_id: null, movies: [] }
    moviesData.value = []
    return
  }

  loading.value = true
  error.value = ''
  try {
    const data = await apiGet(`${BACKEND_API_URL}/lists/${route.params.id}`)
    list.value = data

    if (data.movies && data.movies.length > 0) {
      const promises = data.movies.map(async (movieItem) => {
        let idForApiCall;

        if (typeof movieItem === 'object' && movieItem !== null) {
          if (movieItem.tmdb_id !== undefined && typeof movieItem.tmdb_id !== 'object') {
            idForApiCall = movieItem.tmdb_id;
          } else if (movieItem.id !== undefined && typeof movieItem.id !== 'object') {
            idForApiCall = movieItem.id;
          }
        } else if (typeof movieItem === 'string' || typeof movieItem === 'number') {
          idForApiCall = movieItem;
        }

        if (idForApiCall === undefined || idForApiCall === null || String(idForApiCall).trim() === '' || typeof idForApiCall === 'object') {
          console.error(t('listDetails.error.invalidTmdbIdConsole'), movieItem, 'ID extraído:', idForApiCall);
          return null;
        }

        try {
          const movieDetails = await apiGet(`${API_BASE_URL}/movie/${idForApiCall}`);
          return movieDetails;
        } catch (e) {
          console.error(t('listDetails.error.fetchTmdbMovieConsole', { id: idForApiCall, message: e.message }), 'Item original:', movieItem);
          return null;
        }
      });
      moviesData.value = (await Promise.all(promises)).filter(Boolean);
    } else {
      moviesData.value = []
    }
  } catch (e) {
    error.value = e.message || t('listDetails.error.fetchListDetails')
    list.value = { id: null, name: '', is_main: false, user_id: null, movies: [] }
    moviesData.value = []
  } finally {
    loading.value = false
  }
}

watch(() => route.params.id, (newId) => {
  if (newId) {
    fetchListDetails()
  }
})

watch(() => authStore.isAuthenticated, (newIsAuthenticated) => {
  if (route.params.id) {
    fetchListDetails()
  }
}, { immediate: true })

async function handleRemoveFromList(tmdbId) {
  if (!authStore.isAuthenticated || !list.value.id) return;
  try {
    await apiDelete(`${BACKEND_API_URL}/lists/${list.value.id}/movies/${tmdbId}`);
    await fetchListDetails();
  } catch (e) {
    error.value = e.message || t('listDetails.error.removeMovie');
  }
}

function shareListLink() {
  const publicUrl = `${window.location.origin}/listas/publica/${list.value.id}`;
  if (navigator.clipboard) {
    navigator.clipboard.writeText(publicUrl).then(() => {
      alert(t('listDetails.share.success'));
    }, () => {
      window.prompt(t('listDetails.share.prompt'), publicUrl);
    });
  } else {
    window.prompt(t('listDetails.share.prompt'), publicUrl);
  }
}

</script>

<style scoped>
/* Most styling now handled by Bootstrap classes */
/* Custom spacing between badge and ID */
.gap-3 {
  gap: 1rem;
}
</style>
