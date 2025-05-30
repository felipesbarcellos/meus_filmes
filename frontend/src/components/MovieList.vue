<template>
  <div class="row row-cols-2 row-cols-sm-3 row-cols-md-4 row-cols-lg-5 row-cols-xl-6 g-3 g-md-4">
    <div v-for="movie in movies" :key="movie.id" class="col">
      <div class="h-100 d-flex flex-column">
        <MovieCard :movie="movie" class="flex-grow-1" />
        <template v-if="showWatchedActions && movie.watched_at">
          <div class="card-footer p-2 bg-secondary bg-opacity-25">
            <div class="d-flex justify-content-around">
              <button @click.stop="emitUpdateDate(movie.id)" class="btn btn-sm btn-outline-info p-1 flex-grow-1 me-1" :title="$t('movieList.actions.updateDateTitle')">
                <i class="bi bi-calendar-event"></i> {{ $t('movieList.actions.edit') }}
              </button>
              <button @click.stop="emitDelete(movie.id)" class="btn btn-sm btn-outline-danger p-1 flex-grow-1 ms-1" :title="$t('movieList.actions.removeFromWatchedTitle')">
                <i class="bi bi-trash"></i> {{ $t('movieList.actions.delete') }}
              </button>
            </div>
            <div v-if="movieToUpdateDate === movie.id" class="mt-2">
              <input type="date" v-model="newWatchedDate" class="form-control form-control-sm bg-dark text-light border-secondary" />
              <button @click.stop="confirmUpdateDate(movie.id)" class="btn btn-sm btn-success w-100 mt-1">{{ $t('movieList.actions.confirmDate') }}</button>
            </div>
          </div>
        </template>
        <template v-if="showRemoveFromList">
          <div class="card-footer p-2 bg-secondary bg-opacity-10">
            <button @click.stop="emitRemoveFromList(movie.id)" class="btn btn-sm btn-outline-warning w-100">
              <i class="bi bi-x-circle"></i> {{ $t('movieList.actions.delete') }}
            </button>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { apiGet } from '@/utils/api'
import MovieCard from './MovieCard.vue'

const { t, locale } = useI18n() // Initialize t

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

// Se MovieList for responsável por buscar os filmes, adicione lógica semelhante ao MovieDetails
// Caso contrário, o componente pai deve garantir que os filmes estejam no idioma correto

// Exemplo de recarregar filmes ao trocar idioma (caso MovieList busque os filmes):
// watch(locale, () => { fetchMoviesNoComponentePai() })

// Se MovieList só exibe, não busca, não precisa alterar nada além do alt/title
</script>

<style scoped>
.movie-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

.card-footer {
  border-top: 1px solid rgba(255, 255, 255, 0.125);
  background-clip: padding-box;
  z-index: 2;
}

.col {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.h-100 {
  height: 100% !important;
}

.flex-grow-1 {
  flex-grow: 1 !important;
}

/* Remove absolute positioning from footers */
</style>