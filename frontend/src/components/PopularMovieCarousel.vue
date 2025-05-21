<template>
  <div class="container-fluid bg-dark rounded shadow-lg py-3 py-md-4 px-2 px-md-4 my-3 my-md-4">
    <h2 class="h4 h3-md mb-3 mb-md-4 text-light">Filmes Populares</h2>
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Carregando...</span>
      </div>
      <p class="mt-2 text-secondary">Carregando</p>
    </div>
    
    <div v-else-if="error" class="alert alert-danger text-center" role="alert">
      Erro ao carregar filmes.
    </div>
    <div v-else>
      <div class="d-flex align-items-center">
        <button class="btn btn-outline-primary rounded-circle me-2 me-md-3 carousel-nav flex-shrink-0" 
                @click="prev" 
                :disabled="currentIndex === 0">
          <span>&laquo;</span>
        </button>
        
        <div class="d-flex flex-nowrap overflow-hidden carousel-container flex-grow-1">
          <div v-for="(movie, idx) in visibleMovies"
               :key="movie.id"
               class="card bg-dark border-dark text-light mx-1 mx-sm-2 movie-card"
               @click="goToDetails(movie.id)">
            <div class="position-relative poster-wrapper">
              <img :src="getPosterUrl(movie.poster_path)" 
                   :alt="movie.title" 
                   class="card-img-top movie-poster" />
                   <div class="position-absolute top-0 end-0 m-2 badge bg-dark movie-rating">
                <span>{{ movie.vote_average ? movie.vote_average.toFixed(1) : 'N/A' }}</span>
                <span class="text-warning ms-1">★</span>
              </div>
              
              <div v-if="movie.release_date" class="position-absolute bottom-0 start-0 m-2 badge bg-dark movie-year">
                {{ movie.release_date.substring(0, 4) }}
              </div>
            </div>
            
            <div class="card-body p-2 text-center">
              <h6 class="card-title mb-0">{{ movie.title }}</h6>
            </div>
          </div>      
        </div>
        
        <button class="btn btn-outline-primary rounded-circle ms-2 ms-md-3 carousel-nav flex-shrink-0" 
                @click="next" 
                :disabled="currentIndex + visibleCount >= movies.length">
          <span>&raquo;</span>
        </button>
      </div>
      <div class="text-center mt-3">
        <RouterLink to="/popular-movies" class="btn btn-outline-light btn-sm">
          Ver mais filmes populares
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRouter, RouterLink } from 'vue-router' // Added RouterLink
import { apiGet } from '@/utils/api'

const API_BASE_URL = '/api/tmdb' // URL base do seu backend para TMDB

const movies = ref([])
const loading = ref(true)
const error = ref(false)
const currentIndex = ref(0)
const router = useRouter()
const windowWidth = ref(window.innerWidth)

// Ajustar quantidade de filmes visíveis baseado no tamanho da tela
const visibleCount = computed(() => {
  if (windowWidth.value < 576) return 2      // Dispositivos muito pequenos
  if (windowWidth.value < 768) return 3      // Celulares
  if (windowWidth.value < 992) return 4      // Tablets
  if (windowWidth.value < 1200) return 5   // Tablets grandes
  if (windowWidth.value < 1400) return 6   // Laptops pequenos
  if (windowWidth.value < 1600) return 7   // Laptops grandes
  if (windowWidth.value < 1800) return 8   // Laptops muito grandes
  if (windowWidth.value < 2000) return 9   // Monitores pequenos
})

// Detectar mudanças na largura da tela
const handleResize = () => {
  windowWidth.value = window.innerWidth
  // Garantir que o currentIndex esteja dentro dos limites ao redimensionar
  if (currentIndex.value + visibleCount.value > movies.value.length) {
    currentIndex.value = Math.max(0, movies.value.length - visibleCount.value)
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  fetchMovies()
})

const fetchMovies = async () => {
  loading.value = true
  error.value = false
  try {
    // apiGet já retorna o JSON, não precisa .json()
    const data = await apiGet(`${API_BASE_URL}/popular?page=1`)
    movies.value = data.results || []
  } catch (e) {
    error.value = true
    console.error("Erro ao buscar filmes populares:", e.message)
  } finally {
    loading.value = false
  }
}

const visibleMovies = computed(() => {
  return movies.value.slice(currentIndex.value, currentIndex.value + visibleCount.value)
})

function next() {
  if (currentIndex.value + visibleCount.value < movies.value.length) {
    currentIndex.value++
  }
}
function prev() {
  if (currentIndex.value > 0) {
    currentIndex.value--
  }
}
function getPosterUrl(path) {
  return path ? `https://image.tmdb.org/t/p/w300${path}` : ''
}

function goToDetails(id) {
  router.push(`/movie/${id}`)
}

// Limpar event listener ao desmontar o componente
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
/* Custom styles to complement Bootstrap */
.carousel-container {
  scroll-behavior: smooth;
  padding: 0.5rem 0;
}

.movie-card {
  width: 145px; /* Base size - smaller to accommodate more cards */
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.movie-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 0.5rem 1rem rgba(var(--bs-primary-rgb), 0.3) !important;
}

.poster-wrapper {
  aspect-ratio: 2/3;
  overflow: hidden;
}

.movie-poster {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.movie-card:hover .movie-poster {
  transform: scale(1.04);
}

.movie-rating, .movie-year {
  background-color: rgba(0, 0, 0, 0.7) !important;
  backdrop-filter: blur(8px);
  transition: all 0.2s ease;
}

.movie-card:hover .movie-rating {
  background-color: rgba(var(--bs-success-rgb), 0.9) !important;
}

.movie-card:hover .movie-year {
  background-color: rgba(var(--bs-primary-rgb), 0.9) !important;
}

.carousel-nav {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Responsive adjustments */
@media (max-width: 992px) {
  .movie-card {
    width: 160px;
  }
}

@media (max-width: 768px) {
  .movie-card {
    width: 140px;
  }
  
  .card-body {
    padding: 0.5rem !important;
  }
  
  h6.card-title {
    font-size: 0.9rem;
  }
}

@media (max-width: 576px) {
  .movie-card {
    width: 120px;
  }
  
  .carousel-nav {
    width: 32px;
    height: 32px;
    padding: 0.15rem;
  }
  
  h6.card-title {
    font-size: 0.8rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .container-fluid {
    padding-left: 0.5rem !important;
    padding-right: 0.5rem !important;
  }
  
  .movie-rating, .movie-year {
    font-size: 0.7rem;
    padding: 0.2rem 0.4rem;
  }
}

@media (max-width: 400px) {
  .movie-card {
    width: 110px;
  }
  
  .mx-1 {
    margin-left: 0.15rem !important;
    margin-right: 0.15rem !important;
  }
}
</style>
