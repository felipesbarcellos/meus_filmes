<template>
  <div class="container py-4">
    <h1 class="mb-4 text-light">Filmes Populares</h1>

    <div v-if="loading && movies.length === 0" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Carregando...</span>
      </div>
      <p class="mt-3 text-secondary">Carregando filmes populares...</p>
    </div>

    <div v-else-if="error" class="alert alert-danger" role="alert">
      {{ error }}
    </div>

    <div v-else-if="movies.length === 0 && !loading" class="alert alert-secondary text-center">
      Nenhum filme popular encontrado no momento.
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
import { ref, onMounted } from 'vue'; 
import MovieList from '@/components/MovieList.vue';
import PaginationControls from '@/components/PaginationControls.vue'; // Import the new component
import { apiGet } from '@/utils/api';

const movies = ref([]);
const loading = ref(true);
const error = ref('');
const currentPage = ref(1);
const totalPages = ref(0); // To store the total number of pages from API

const API_BASE_URL = '/api/tmdb';

async function fetchPopularMovies(page = 1) {
  loading.value = true;
  error.value = '';
  // Clear movies only if it's a direct page load, not for subsequent loading states of the same page
  // movies.value = []; // Let's keep old movies visible while new ones load for a better UX
  try {
    const data = await apiGet(`${API_BASE_URL}/popular?page=${page}`);
    if (data && data.results) {
      movies.value = data.results;
      totalPages.value = data.total_pages || 0;
      currentPage.value = data.page || page; // Ensure currentPage reflects the API's response
    } else {
      movies.value = [];
      totalPages.value = 0;
      console.warn('Popular movies response did not contain results or total_pages:', data);
      error.value = 'Resposta da API inválida ao buscar filmes populares.';
    }
  } catch (e) {
    console.error('Erro ao buscar filmes populares na página', page, ':', e);
    error.value = e.message || 'Falha ao carregar filmes populares. Tente novamente mais tarde.';
    // movies.value = []; // Keep existing movies on error if any
    // totalPages.value = 0; // Keep existing totalPages on error if any
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
