<template>  <div class="container mt-4 mb-5">
    <div class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center mb-4 gap-2">
      <h2 class="h3 mb-2 mb-md-0">{{ $t('genreMovies.title') }}<span class="text-primary fw-bold">{{ genreName }}</span></h2>
      <button class="btn btn-outline-secondary btn-sm" @click="router.back()">{{ $t('genreMovies.backButton') }}</button>
    </div>

    <div v-if="loading && movies.length === 0" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">{{ $t('general.loading') }}</span>
      </div>
      <p class="mt-2">{{ $t('general.loading') }}</p>
    </div>
    <div v-else-if="error" class="alert alert-danger text-center" role="alert">
      {{ $t('genreMovies.loadingError') }}
    </div>
    <div v-else-if="movies.length === 0" class="alert alert-info text-center" role="alert">
      {{ $t('genreMovies.noMoviesFound') }}
    </div>
    <div v-else>
      <div class="row row-cols-2 row-cols-sm-2 row-cols-md-3 row-cols-lg-4 row-cols-xl-5 g-2 g-md-3 g-lg-4">
        <div v-for="movie in movies" :key="movie.id" class="col">
          <div class="card h-100 shadow-sm movie-card-custom" @click="goToMovie(movie.id)">
            <img :src="getPosterUrl(movie.poster_path)" class="card-img-top movie-poster-custom" :alt="movie.title" />
            <div class="card-body d-flex flex-column p-2 p-md-3">
              <h5 class="card-title text-center movie-title-custom flex-grow-1 fs-6">{{ movie.title }}</h5>
            </div>
          </div>
        </div>
      </div>
      <PaginationControls
        :current-page="page"
        :total-pages="totalPages"
        :has-more="hasMore"
        :loading="loading"
        @page-changed="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n'; // Import useI18n
import { apiGet } from '@/utils/api';
import PaginationControls from '@/components/PaginationControls.vue';

const { t } = useI18n(); // Initialize t function

const API_BASE_URL = '/api/tmdb'
const route = useRoute()
const router = useRouter()
const movies = ref([])
const loading = ref(true)
const error = ref(false)
const genreName = ref('')
const page = ref(1)
const hasMore = ref(true)
const totalPages = ref(0); // Add totalPages

const fetchMoviesByGenre = async () => {
  loading.value = true
  error.value = false
  try {
    const genreId = route.params.id
    genreName.value = route.query.name || ''
    const data = await apiGet(`${API_BASE_URL}/discover/movie?with_genres=${genreId}&page=${page.value}`)
    if (!data || !Array.isArray(data.results)) {
      throw new Error('Resposta inesperada da API de filmes.')
    }
    movies.value = data.results
    totalPages.value = data.total_pages || 0; // Store total_pages
    hasMore.value = !!data.total_pages && page.value < data.total_pages
  } catch (e) {
    error.value = true
    movies.value = []
    console.error("Erro ao buscar filmes por gênero:", e)
  } finally {
    loading.value = false
  }
}

function getPosterUrl(path) {
  return path ? `https://image.tmdb.org/t/p/w300${path}` : ''
}

function goToMovie(id) {
  router.push(`/movie/${id}`)
}

function handlePageChange(newPage) { // Renamed from changePage
  if (newPage < 1 || newPage === page.value) return;
  page.value = newPage;
  fetchMoviesByGenre();
}

watch(() => route.params.id, () => {
  page.value = 1
  totalPages.value = 0; // Reset totalPages on genre change
  fetchMoviesByGenre()
})

onMounted(fetchMoviesByGenre)
</script>

<style scoped>
/* Removed most styles as Bootstrap is now used. */
/* Custom styles for specific component needs can be added here if Bootstrap doesn't cover them. */

.movie-card-custom {
  cursor: pointer;
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
  background-color: var(--bs-gray-800); /* Assuming a dark theme, adjust if needed */
  color: var(--bs-light);
  border: 1px solid var(--bs-gray-700);
}

.movie-card-custom:hover {
  transform: translateY(-5px) scale(1.03);
  box-shadow: 0 0.5rem 1rem rgba(var(--bs-primary-rgb), 0.25) !important; /* Using Bootstrap primary color for hover shadow */
}

.movie-poster-custom {
  aspect-ratio: 2/3;
  object-fit: cover;
  border-top-left-radius: var(--bs-card-inner-border-radius);
  border-top-right-radius: var(--bs-card-inner-border-radius);
}

.movie-title-custom {
  font-size: 0.85rem; /* Reduzido para melhor visualização em dispositivos móveis */
  min-height: 2.5em; /* Ensure consistent title height */
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.2;
}

/* Responsive adjustments */
@media (max-width: 767px) {
  .movie-title-custom {
    font-size: 0.75rem;
  }
}

@media (min-width: 768px) {
  .movie-title-custom {
    font-size: 0.85rem;
  }
}

@media (min-width: 992px) {
  .movie-title-custom {
    font-size: 1rem;
  }
}

/* Styling for loading, error, empty states if specific visual is needed beyond Bootstrap defaults */
.loading, .error, .empty {
  text-align: center;
  margin: 2rem 0;
  font-size: 1.2rem;
}

.text-primary {
  color: var(--bs-primary) !important; /* Ensure Bootstrap primary color is used */
}

</style>
