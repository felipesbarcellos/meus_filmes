<template>
  <div class="container-fluid py-3 py-md-4 bg-dark rounded shadow-sm mb-3 mb-md-4">
    <h2 class="h5 h4-md mb-2 mb-md-3 text-light">Gêneros</h2>
    
    <div v-if="loading" class="text-center py-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Carregando...</span>
      </div>
      <p class="mt-2 text-secondary">Carregando</p>
    </div>
    
    <div v-else-if="error" class="alert alert-danger py-2" role="alert">
      {{ error }}
    </div>
      <div v-else class="d-flex align-items-center w-100">
      <button class="btn btn-sm btn-outline-primary rounded-circle me-1 me-md-2 flex-shrink-0 nav-btn" 
              @click="prev" 
              :disabled="currentIndex === 0">
        <span aria-hidden="true">&laquo;</span>
      </button>
      
      <div class="d-flex flex-nowrap overflow-hidden flex-grow-1">
        <div v-for="genre in visibleGenres"
             :key="genre.id"
             class="genre-card mx-2"
             @click="goToGenre(genre)">
          <div class="genre-name py-2 px-3">{{ genre.name }}</div>
        </div>      </div>
      
      <button class="btn btn-sm btn-outline-primary rounded-circle ms-1 ms-md-2 flex-shrink-0 nav-btn" 
              @click="next" 
              :disabled="currentIndex + visibleCount.value >= genres.length">
        <span aria-hidden="true">&raquo;</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { apiGet } from '@/utils/api'

const props = defineProps({
  type: {
    type: String,
    default: 'movies', // 'movies' ou 'tv'
    validator: v => ['movies', 'tv'].includes(v)
  }
})

const API_BASE_URL = '/api/tmdb'

const genres = ref([])
const loading = ref(true)
const error = ref('')
const currentIndex = ref(0)
const windowWidth = ref(window.innerWidth)

// Ajustar quantidade de gêneros visíveis com base no tamanho da tela
const visibleCount = computed(() => {
  if (windowWidth.value < 400) return 2    // Celulares muito pequenos
  if (windowWidth.value < 576) return 3    // Celulares
  if (windowWidth.value < 768) return 4    // Tablets pequenos
  if (windowWidth.value < 992) return 5    // Tablets
  return 6                                // Desktop
})

// Detectar mudanças na largura da tela
const handleResize = () => {
  windowWidth.value = window.innerWidth
  // Garantir que o currentIndex esteja dentro dos limites ao redimensionar
  if (currentIndex.value + visibleCount.value > genres.value.length) {
    currentIndex.value = Math.max(0, genres.value.length - visibleCount.value)
  }
}

const fetchGenres = async () => {
  loading.value = true
  error.value = ''
  try {
    const endpoint = props.type === 'tv' ? 'tv/genres' : 'movie/genres'
    const data = await apiGet(`${API_BASE_URL}/${endpoint}`)
    if (!data || !Array.isArray(data.genres)) {
      throw new Error('Resposta inesperada da API de gêneros.')
    }
    genres.value = data.genres
  } catch (e) {
    error.value = e.message || 'Erro ao buscar gêneros.'
    genres.value = []
    console.error('Erro ao buscar gêneros:', e)
  } finally {
    loading.value = false
  }
}

const visibleGenres = computed(() => {
  return genres.value.slice(currentIndex.value, currentIndex.value + visibleCount.value)
})

function next() {
  if (currentIndex.value + visibleCount.value < genres.value.length) {
    currentIndex.value++
  }
}
function prev() {
  if (currentIndex.value > 0) {
    currentIndex.value--
  }
}

const router = useRouter()
function goToGenre(genre) {
  router.push({ path: `/genre/${genre.id}`, query: { name: genre.name } })
}

watch(() => props.type, fetchGenres)

onMounted(() => {
  window.addEventListener('resize', handleResize)
  fetchGenres()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
/* Custom styles to complement Bootstrap */
.genre-card {
  min-width: 110px;
  background-color: var(--bs-gray-800);
  border-radius: 8px;
  border: 1px solid var(--bs-gray-700);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
  margin-bottom: 0.5rem;
  flex-grow: 1; /* Permite cards crescerem para usar espaço disponível */
}

.genre-card:hover {
  transform: translateY(-2px) scale(1.03);
  box-shadow: 0 0.25rem 0.75rem rgba(var(--bs-primary-rgb), 0.3);
  background-color: var(--bs-primary);
}

.genre-name {
  color: var(--bs-light);
  font-weight: 500;
  font-size: 0.9rem;
  text-align: center;
  width: 100%;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .genre-card {
    min-width: 90px;
  }
  
  .genre-name {
    font-size: 0.85rem;
    padding: 0.2rem 0.4rem !important;
  }
}

@media (max-width: 576px) {
  .genre-card {
    min-width: 70px;
  }
  
  .nav-btn {
    width: 28px;
    height: 28px;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .genre-name {
    font-size: 0.8rem;
    padding: 0.15rem 0.3rem !important;
  }
}

/* Garantir que o carrossel ocupe todo o espaço horizontal disponível */
.overflow-hidden {
  width: 100%;
}
</style>
