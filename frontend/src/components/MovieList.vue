<template>
  <div class="row row-cols-2 row-cols-sm-3 row-cols-md-4 row-cols-lg-5 row-cols-xl-6 g-3 g-md-4">
    <div v-for="movie in movies" :key="movie.id" class="col">
      <div class="card h-100 bg-dark text-light border-secondary movie-card">
        <div @click="goToMovie(movie.id)" class="clickable-area">
          <div class="position-relative poster-container">
            <img :src="getPosterUrl(movie.poster_path)" :alt="movie.title" class="card-img-top movie-poster" />
            <div class="position-absolute top-0 end-0 m-2 badge bg-dark bg-opacity-75 movie-rating" v-if="movie.vote_average">
              <span>{{ movie.vote_average.toFixed(1) }}</span>
              <span class="text-warning ms-1">★</span>
            </div>
            <div class="position-absolute bottom-0 start-0 m-2 badge bg-dark bg-opacity-75" v-if="movie.release_date">
              {{ movie.release_date.substring(0, 4) }}
            </div>
          </div>
          <div class="card-body p-2 d-flex align-items-center justify-content-center">
            <h6 class="card-title text-center mb-0">{{ movie.title }}</h6>
          </div>
        </div>

        <!-- Watched Actions -->
        <div v-if="showWatchedActions && movie.watched_at" class="card-footer p-2 bg-secondary bg-opacity-25">
          <p class="text-light small mb-1 text-center">{{ $t('movieList.watchedOn') }} {{ formatDate(movie.watched_at) }}</p>
          <div class="d-flex justify-content-around">
            <button @click.stop="emitUpdateDate(movie.id)" class="btn btn-sm btn-outline-info p-1 flex-grow-1 me-1" :title="$t('movieList.actions.updateDateTitle')">
              <i class="bi bi-calendar-event"></i> {{ $t('movieList.actions.edit') }}
            </button>
            <button @click.stop="emitDelete(movie.id)" class="btn btn-sm btn-outline-danger p-1 flex-grow-1 ms-1" :title="$t('movieList.actions.removeFromWatchedTitle')">
              <i class="bi bi-trash"></i> {{ $t('movieList.actions.delete') }}
            </button>
          </div>
          <!-- Input para nova data (inicialmente escondido) -->
          <div v-if="movieToUpdateDate === movie.id" class="mt-2">
            <input type="date" v-model="newWatchedDate" class="form-control form-control-sm bg-dark text-light border-secondary" />
            <button @click.stop="confirmUpdateDate(movie.id)" class="btn btn-sm btn-success w-100 mt-1">{{ $t('movieList.actions.confirmDate') }}</button>
          </div> 
        </div>
        <!-- Remove from List Button -->
        <div v-if="showRemoveFromList" class="card-footer p-2 bg-secondary bg-opacity-10">
          <button @click.stop="emitRemoveFromList(movie.id)" class="btn btn-sm btn-outline-warning w-100">
            <i class="bi bi-x-circle"></i> {{ $t('movieList.actions.delete') }} <!-- Assuming same delete text is fine -->
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n' // Import useI18n

const { t } = useI18n() // Initialize t

const props = defineProps({
  movies: {
    type: Array,
    required: true
  },
  showWatchedActions: {
    type: Boolean,
    default: false
  },
  showRemoveFromList: { // NEW PROP
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['delete-watched', 'update-watched-date', 'remove-from-list']) // NEW EVENT
const router = useRouter()

const movieToUpdateDate = ref(null); // Stores the ID of the movie whose date is being updated
const newWatchedDate = ref(''); // Stores the new date selected by the user


function goToMovie(id) {
  if (movieToUpdateDate.value) return; // Prevent navigation if date input is open
  router.push(`/movie/${id}`)
}

function getPosterUrl(path) {
  return path ? `https://image.tmdb.org/t/p/w300${path}` : ''
}

function formatDate(dateString) {
  if (!dateString) return t('movieList.na'); // N/A translation
  const date = new Date(dateString);
  // Adjust for timezone issues if dateString is YYYY-MM-DD by treating it as UTC
  const utcDate = new Date(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate());
  // TODO: Consider making locale for toLocaleDateString dynamic based on i18n.locale
  return utcDate.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

function emitDelete(tmdbId) {
  emit('delete-watched', tmdbId);
}

function emitUpdateDate(tmdbId) {
  if (movieToUpdateDate.value === tmdbId) {
    movieToUpdateDate.value = null; // Close if already open
    newWatchedDate.value = '';
  } else {
    movieToUpdateDate.value = tmdbId;
    // Find the movie to prefill the date input
    const movie = props.movies.find(m => m.id === tmdbId);
    if (movie && movie.watched_at) {
      // Ensure date is in YYYY-MM-DD for the input
      const dateObj = new Date(movie.watched_at);
      // Adjust for timezone: get parts from UTC date
      const year = dateObj.getUTCFullYear();
      const month = (dateObj.getUTCMonth() + 1).toString().padStart(2, '0');
      const day = dateObj.getUTCDate().toString().padStart(2, '0');
      newWatchedDate.value = `${year}-${month}-${day}`;
    } else {
      newWatchedDate.value = ''; // Clear if no date
    }
  }
}

function confirmUpdateDate(tmdbId) {
  if (!newWatchedDate.value) {
    console.warn(t('movieList.warnings.noDateSelected'));
    return;
  }
  emit('update-watched-date', { tmdbId, newDate: newWatchedDate.value });
  movieToUpdateDate.value = null; // Close the input
  newWatchedDate.value = ''; // Reset the date
}

function emitRemoveFromList(tmdbId) {
  emit('remove-from-list', tmdbId);
}

</script>

<style scoped>
.movie-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  display: flex; /* Ensure footer is part of the card flow */
  flex-direction: column; /* Stack card elements vertically */
}

.clickable-area {
  cursor: pointer;
  flex-grow: 1; /* Allow this area to take available space */
  display: flex;
  flex-direction: column;
}

.movie-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 0.5rem 1rem rgba(var(--bs-primary-rgb), 0.3) !important;
}

.poster-container {
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

.card-body {
  min-height: 3.5rem; /* Ensure consistent card body height */
  flex-grow: 0; /* Prevent card body from growing excessively */
}

.card-footer {
  border-top: 1px solid rgba(255, 255, 255, 0.125); /* Subtle separator */
}

.btn-sm i {
  margin-right: 0.25rem;
}

/* Ensure Bootstrap icons are available if not globally included */
@import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css");
</style>