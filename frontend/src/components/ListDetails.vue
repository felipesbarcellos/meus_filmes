<template>
  <div class="container py-4">
    <div class="card bg-dark text-light shadow mb-4">
      <div class="card-body p-4">
        <div v-if="loading" class="text-center py-4">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Carregando...</span>
          </div>
          <p class="mt-3 text-secondary">Carregando detalhes da lista...</p>
        </div>
        
        <div v-else-if="error" class="alert alert-danger" role="alert">
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
          <div class="d-flex justify-content-end mb-3" v-if="list.id">
            <button class="btn btn-outline-primary btn-sm" @click="shareListLink">
              <i class="bi bi-share"></i> Compartilhar lista
            </button>
          </div>
          <MovieList v-if="moviesData.length > 0" :movies="moviesData" :showRemoveFromList="true" @remove-from-list="handleRemoveFromList" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue' // Adicionado watch
import { useRoute } from 'vue-router'
import MovieList from './MovieList.vue'
import { useAuthStore } from '@/stores/auth' // Importar o store Pinia
import { apiGet, apiDelete } from '@/utils/api' // Adicionado apiDelete

const route = useRoute()
const authStore = useAuthStore() // Usar o store Pinia

const list = ref({ id: null, name: '', is_main: false, user_id: null, movies: [] })
const loading = ref(true)
const error = ref('')
const moviesData = ref([])

const API_BASE_URL = '/api/tmdb'
const BACKEND_API_URL = '/api' // Adicionado para a rota de listas

async function fetchListDetails() {
  if (!authStore.isAuthenticated) {
    // Idealmente, esta rota deveria ser protegida por um navigation guard
    // ou o componente deveria mostrar uma mensagem de "acesso negado"
    error.value = 'Você precisa estar logado para ver os detalhes da lista.'
    loading.value = false
    list.value = { id: null, name: '', is_main: false, user_id: null, movies: [] } // Reseta a lista
    moviesData.value = []
    return
  }

  loading.value = true
  error.value = ''
  try {
    // Usa apiGet para garantir tratamento centralizado de token
    const data = await apiGet(`${BACKEND_API_URL}/lists/${route.params.id}`)
    list.value = data

    if (data.movies && data.movies.length > 0) {
      const promises = data.movies.map(async (movieItem) => { // Renamed tmdb_id to movieItem for clarity
        // Attempt to extract the primitive TMDB ID from the movieItem.
        // The error "[object Object]" implies the original loop variable was an object.
        let idForApiCall;

        if (typeof movieItem === 'object' && movieItem !== null) {
          if (movieItem.tmdb_id !== undefined && typeof movieItem.tmdb_id !== 'object') {
            idForApiCall = movieItem.tmdb_id;
          } else if (movieItem.id !== undefined && typeof movieItem.id !== 'object') {
            // Fallback to 'id' if 'tmdb_id' is not suitable or not present
            idForApiCall = movieItem.id;
          }
        } else if (typeof movieItem === 'string' || typeof movieItem === 'number') {
          // If movieItem itself is already a primitive ID (less likely given the error, but for robustness)
          idForApiCall = movieItem;
        }

        // Validate the extracted ID
        if (idForApiCall === undefined || idForApiCall === null || String(idForApiCall).trim() === '' || typeof idForApiCall === 'object') {
          console.error('Não foi possível extrair um ID TMDB primitivo válido do item:', movieItem, 'ID extraído:', idForApiCall);
          return null; // Skip this item if a valid primitive ID cannot be obtained
        }

        try {
          // Use the extracted primitive idForApiCall
          const movieDetails = await apiGet(`${API_BASE_URL}/movie/${idForApiCall}`);
          return movieDetails;
        } catch (e) {
          console.error(`Erro ao buscar filme TMDB ID ${idForApiCall} para lista: ${e.message}. Item original:`, movieItem);
          return null;
        }
      });
      moviesData.value = (await Promise.all(promises)).filter(Boolean);
    } else {
      moviesData.value = []
    }
  } catch (e) {
    error.value = e.message || 'Erro ao buscar detalhes da lista'
    list.value = { id: null, name: '', is_main: false, user_id: null, movies: [] } // Reseta em caso de erro
    moviesData.value = []
  } finally {
    loading.value = false
  }
}

// Observa mudanças no ID da rota para recarregar os detalhes da lista
watch(() => route.params.id, (newId) => {
  if (newId) {
    fetchListDetails()
  }
})

// Observa o estado de autenticação para recarregar ou limpar os detalhes
watch(() => authStore.isAuthenticated, (newIsAuthenticated) => {
  if (route.params.id) { // Só executa se estiver numa rota de detalhes de lista
    fetchListDetails()
  }
}, { immediate: true }) // `immediate: true` para rodar na montagem inicial

async function handleRemoveFromList(tmdbId) {
  if (!authStore.isAuthenticated || !list.value.id) return;
  try {
    await apiDelete(`${BACKEND_API_URL}/lists/${list.value.id}/movies/${tmdbId}`);
    await fetchListDetails(); // Atualiza a lista após remoção
  } catch (e) {
    error.value = e.message || 'Erro ao remover filme da lista.';
  }
}

function shareListLink() {
  const publicUrl = `${window.location.origin}/listas/publica/${list.value.id}`;
  if (navigator.clipboard) {
    navigator.clipboard.writeText(publicUrl).then(() => {
      alert('Link da lista copiado para a área de transferência!');
    }, () => {
      window.prompt('Copie o link da lista:', publicUrl);
    });
  } else {
    window.prompt('Copie o link da lista:', publicUrl);
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
