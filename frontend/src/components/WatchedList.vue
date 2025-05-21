<template>
  <div class="container bg-dark rounded shadow-lg py-4 px-4 my-4">
    <h2 class="h3 mb-3 text-light">{{ $t('watchedList.title') }}</h2>
    <WatchedStats :count="filteredMovies.length" />
    <div class="card bg-dark border-secondary mb-4 p-3">
      <div class="row g-3 align-items-end">
        <div class="col-md-4">
          <label class="form-label text-light">{{ $t('watchedList.startDate') }}</label>
          <input type="date" v-model="filterStartDate" class="form-control bg-dark text-light border-secondary" />
        </div>
        <div class="col-md-4">
          <label class="form-label text-light">{{ $t('watchedList.endDate') }}</label>
          <input type="date" v-model="filterEndDate" class="form-control bg-dark text-light border-secondary" />
        </div>
        <div class="col-md-4">
          <button @click="filterStartDate = ''; filterEndDate = ''; filterMonth = ''" 
                  class="btn btn-primary w-100">
            {{ $t('watchedList.clearFilters') }}
          </button>
        </div>
      </div>
    </div>
    <div v-if="loading" class="text-center py-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">{{ $t('watchedList.loading.srOnly') }}</span>
      </div>
      <p class="mt-2 text-primary">{{ $t('watchedList.loading.text') }}</p>
    </div>
    <div v-else-if="error" class="alert alert-danger" role="alert">
      {{ error }}
    </div>
    <div v-else-if="filteredMovies.length === 0" class="alert alert-secondary text-center">
      {{ $t('watchedList.noMovies') }}
    </div>
    <MovieList v-else :movies="filteredMovies" :show-watched-actions="true" @delete-watched="handleDeleteWatched" @update-watched-date="handleUpdateWatchedDate" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import MovieList from './MovieList.vue'
import WatchedStats from './WatchedStats.vue'
import { useAuthStore } from '@/stores/auth'
import { apiGet, apiPost, apiDelete } from '@/utils/api'

const { t } = useI18n()

const loading = ref(true)
const error = ref('')
const movies = ref([])

const authStore = useAuthStore() // Usar o store Pinia

// Filtro
const filterMonth = ref('')
const filterStartDate = ref('')
const filterEndDate = ref('')

const API_BASE_URL = '/api/tmdb'
const BACKEND_API_URL = '/api' // Adicionado para a rota de filmes assistidos

const filteredMovies = computed(() => {
  let filtered = movies.value

  // Filtro por data
  if (filterStartDate.value) {
    const start = new Date(filterStartDate.value)
    if (isNaN(start.getTime())) {
      // Handle invalid start date, maybe clear filter or show error
    } else {
      filtered = filtered.filter(m => {
        if (!m.watched_at) return false;
        const watchedDate = new Date(m.watched_at);
        return !isNaN(watchedDate.getTime()) && watchedDate >= start;
      });
    }
  }

  if (filterEndDate.value) {
    const end = new Date(filterEndDate.value)
    if (isNaN(end.getTime())) {
      // Handle invalid end date
    } else {
      filtered = filtered.filter(m => {
        if (!m.watched_at) return false;
        const watchedDate = new Date(m.watched_at);
        // Add 1 day to end date to make it inclusive of the selected day
        const inclusiveEndDate = new Date(end.getFullYear(), end.getMonth(), end.getDate() + 1);
        return !isNaN(watchedDate.getTime()) && watchedDate < inclusiveEndDate;
      });
    }
  }


  // Filtro por mês
  if (filterMonth.value) {
    const now = new Date();
    // Ensure filterMonth.value is a valid number for months
    const numMonths = parseInt(filterMonth.value);
    if (!isNaN(numMonths) && numMonths > 0) {
      const targetDate = new Date(now.getFullYear(), now.getMonth() - numMonths, now.getDate());
      filtered = filtered.filter(m => {
        if (!m.watched_at) return false; // Exclude if no watched_at date
        const watchedDate = new Date(m.watched_at);
        return !isNaN(watchedDate.getTime()) && watchedDate >= targetDate;
      });
    }
  }
  return filtered;
})


async function fetchWatchedMovies() {
  if (!authStore.isAuthenticated || !authStore.user?.id) {
    movies.value = []
    loading.value = false
    return
  }
  loading.value = true
  error.value = ''
  try {
    // Usa apiGet para garantir tratamento centralizado de token
    const data = await apiGet(`${BACKEND_API_URL}/movie/watched/`)
    const watchedItems = data.watched || []
    const detailedMoviesPromises = watchedItems.map(async (item) => {
      try {
        // Usa apiGet para buscar detalhes do filme TMDB
        const movieDetails = await apiGet(`${API_BASE_URL}/movie/${item.tmdb_id}`)
        return {
          ...movieDetails,
          id: movieDetails.id || item.tmdb_id,
          watched_at: item.watched_at
        }
      } catch (e) {
        console.error(`Error fetching details for movie ${item.tmdb_id}:`, e)
        return { tmdb_id: item.tmdb_id, watched_at: item.watched_at, title: 'Erro ao buscar detalhes', error: true };
      }
    })
    const resolvedDetailedMovies = await Promise.all(detailedMoviesPromises);
    movies.value = resolvedDetailedMovies.filter(movie => movie !== null);
    const DIAGNOSTIC_LIMIT = 20;
    if (movies.value.length > DIAGNOSTIC_LIMIT) {
      // console.log(`Displaying first ${DIAGNOSTIC_LIMIT} of ${movies.value.length} watched movies with full details.`);
    }
  } catch (e) {
    error.value = e.message || 'Erro ao buscar filmes assistidos'
    movies.value = []
  } finally {
    loading.value = false
  }
}

async function handleDeleteWatched(tmdbId) {
  if (!authStore.isAuthenticated || !authStore.user?.id) {
    error.value = "Autenticação necessária para remover filme.";
    return;
  }
  try {
    await apiDelete(`${BACKEND_API_URL}/movie/watched/${tmdbId}`);
    // Refresh the list
    await fetchWatchedMovies(); 
  } catch (e) {
    console.error(`Erro ao remover filme ${tmdbId} da lista de assistidos:`, e);
    error.value = e.message || 'Erro ao remover filme dos assistidos.';
  }
}

async function handleUpdateWatchedDate(payload) {
  const { tmdbId, newDate } = payload;
  if (!authStore.isAuthenticated || !authStore.user?.id) {
    error.value = "Autenticação necessária para atualizar data.";
    return;
  }
  if (!newDate) {
    error.value = "Por favor, selecione uma nova data.";
    return;
  }
  try {
    await apiPost(`${BACKEND_API_URL}/movie/watched/`, { 
      tmdb_id: tmdbId, 
      watched_at: newDate 
    });
    // Refresh the list
    await fetchWatchedMovies();
  } catch (e) {
    console.error(`Erro ao atualizar data do filme ${tmdbId}:`, e);
    error.value = e.message || 'Erro ao atualizar data do filme.';
  }
}

onMounted(() => {}); // Corrected closing for onMounted

// Observa o estado de autenticação para buscar/limpar filmes assistidos
watch(() => authStore.isAuthenticated, (newIsAuthenticated) => {
  fetchWatchedMovies() // A própria função já verifica a autenticação
  if (!newIsAuthenticated) {
    // Limpar filtros também pode ser uma boa ideia ao deslogar
    filterStartDate.value = ''
    filterEndDate.value = ''
    filterMonth.value = ''
  }
}, { immediate: true }) // `immediate: true` para rodar na montagem inicial

</script>

<style scoped>
/* Custom styles to complement Bootstrap */
.watched-date-badge {
  position: relative;
  z-index: 1;
}

/* Fix for date inputs to match dark theme */
input[type="date"] {
  color-scheme: dark;
}

/* Transition for hover effects */
.btn-primary {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 0.5rem 1rem rgba(var(--bs-primary-rgb), 0.3);
}
</style>
