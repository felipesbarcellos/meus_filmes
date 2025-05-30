<template>
  <div class="card h-100 bg-dark text-light border-secondary movie-card" @click="goToMovie(movie.id)">
    <div class="position-relative poster-container bg-dark">
      <img :src="getPosterUrl(movie.poster_path)" :alt="movie.title" class="card-img-top movie-poster" v-if="movie.poster_path" />
      <div v-else class="d-flex justify-content-center align-items-center h-100 text-secondary">
        {{ $t('movieCard.noImage') }}
      </div>
      <div class="position-absolute top-0 end-0 m-2 badge bg-dark bg-opacity-75 movie-rating" v-if="movie.vote_average">
        <span>{{ movie.vote_average.toFixed(1) }}</span>
        <span class="text-warning ms-1">★</span>
      </div>
      <div class="position-absolute bottom-0 start-0 m-2 badge bg-dark bg-opacity-75" v-if="movie.release_date">
        {{ movie.release_date.substring(0, 4) }}
      </div>
    </div>
    <div class="card-body p-2 d-flex align-items-center justify-content-center flex-column">
      <h6 class="card-title text-center mb-0">{{ movie.title }}</h6>
      <p v-if="movie.watched_at" class="watched-date text-info small mt-1 mb-0">
        {{ $t('movieList.watchedOn') }} {{ formatDate(movie.watched_at) }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  movie: { type: Object, required: true }
})
const router = useRouter()
const { t } = useI18n()

function goToMovie(id) {
  router.push(`/movie/${id}`)
}
function getPosterUrl(path) {
  return path ? `https://image.tmdb.org/t/p/w300${path}` : ''
}
function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  const utcDate = new Date(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate())
  return utcDate.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' })
}
</script>

<style scoped>
.movie-card {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.movie-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 20px rgba(var(--bs-primary-rgb), 0.3);
}
.poster-container {
  aspect-ratio: 2 / 3;
  overflow: hidden;
}
.movie-poster {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.movie-rating {
  font-size: 1rem;
}
.watched-date {
  font-size: 0.85rem;
  color: #0dcaf0 !important;
  text-align: center;
  width: 100%;
}
</style>
