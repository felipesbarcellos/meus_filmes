<template>
  <div class="container py-4">
    <h1 class="mb-4 text-light">{{ $t('popularMovies.title') }}</h1>

    <div v-if="loading && movies.length === 0" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">{{ $t('general.loading') }}</span>
      </div>
      <p class="mt-3 text-secondary">{{ $t('popularMovies.loadingMessage') }}</p>
    </div>

    <div v-else-if="error" class="alert alert-danger" role="alert">
      {{ error }} <!-- API error messages might need specific handling or generic keys -->
    </div>

    <div v-else-if="movies.length === 0 && !loading" class="alert alert-secondary text-center">
      {{ $t('popularMovies.noMoviesFound') }}
    </div>

    <div v-else>
      <MovieList :movies="movies" />

      <PaginationControls
        :current-page="currentPage"
        :total-pages="totalPages"
        :has-more="currentPage < totalPages" 
        :loading="loading"
        @page-changed="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'; 
import MovieList from '@/components/MovieList.vue';
import PaginationControls from '@/components/PaginationControls.vue';
import { apiGet } from '@/utils/api';
import { useI18n } from 'vue-i18n'; // Import useI18n

const { t, locale } = useI18n(); // Initialize t and locale

const movies = ref([]);
const loading = ref(true);
const error = ref('');
const currentPage = ref(1);
const totalPages = ref(0); // To store the total number of pages from API

const API_BASE_URL = '/api/tmdb';

async function fetchPopularMovies(page = 1) {
  loading.value = true;
  error.value = '';
  try {
    const lang = locale.value === 'en' ? 'en-US' : 'pt-BR';
    const data = await apiGet(`${API_BASE_URL}/popular?page=${page}&language=${lang}`);
    if (data && data.results) {
      movies.value = data.results;
      totalPages.value = data.total_pages || 0;
      currentPage.value = data.page || page;
    } else {
      movies.value = [];
      totalPages.value = 0;
      console.warn('Popular movies response did not contain results or total_pages:', data);
      error.value = t('popularMovies.invalidResponse');
    }
  } catch (e) {
    console.error('Erro ao buscar filmes populares na página', page, ':', e);
    error.value = e.message || t('popularMovies.loadFailure');
  } finally {
    loading.value = false;
  }
}

function handlePageChange(newPage) {
  if (newPage === currentPage.value) return;
  fetchPopularMovies(newPage);
}

onMounted(() => {
  fetchPopularMovies(currentPage.value);
});

watch(locale, () => {
  fetchPopularMovies(currentPage.value);
});

// Optional: Watch for route query changes if you plan to support page numbers in URL
// import { useRoute } from 'vue-router';
// const route = useRoute();
// watch(() => route.query.page, (newPage) => {
//   const pageNum = parseInt(newPage, 10);
//   if (pageNum && pageNum !== currentPage.value) {
//     fetchPopularMovies(pageNum);
//   }
// });

</script>

<style scoped>
/* Scoped styles for PopularMoviesPage */
.container {
  max-width: 1200px; /* Or your preferred max width */
}

.btn i {
  margin-right: 0.25rem;
  margin-left: 0.25rem;
}
</style>
