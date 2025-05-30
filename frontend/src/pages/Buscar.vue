<template>
  <div class="container py-4">
    <form @submit.prevent="triggerSearchNow" class="row mb-4 p-4 bg-dark rounded shadow">
      <div class="col-md-10 mb-2 mb-md-0 position-relative">
        <input 
          type="text" 
          v-model="query" 
          :placeholder="$t('search.placeholder')" 
          class="form-control form-control-lg bg-dark text-light border-secondary"
          @blur="handleInputBlur"
          @focus="handleInputFocus"
          aria-autocomplete="list"
          aria-controls="suggestions-list"
          :aria-expanded="showSuggestionsList && suggestions.length > 0 && query.trim()"
        />
        <!-- Suggestions List -->
        <ul 
          v-if="showSuggestionsList && suggestions.length > 0 && query.trim()" 
          class="list-group position-absolute w-100 mt-1" 
          id="suggestions-list"
          style="z-index: 1000; max-height: 300px; overflow-y: auto;" 
          role="listbox"
        >
          <li 
            v-for="suggestion in suggestions" 
            :key="suggestion.id" 
            class="list-group-item list-group-item-action bg-dark text-light border-secondary suggestion-item"
            @click="selectSuggestion(suggestion)"
            role="option"
            tabindex="0"
            @keydown.enter="selectSuggestion(suggestion)"
            @keydown.space="selectSuggestion(suggestion)"
          >
            {{ suggestion.title }}
            <small v-if="suggestion.release_date && suggestion.release_date.length >= 4" class="text-muted ms-2">({{ $t('search.releaseYear') }} {{ suggestion.release_date.substring(0,4) }})</small>
          </li>
        </ul>
        <!-- Loading Suggestions Indicator -->
        <div 
          v-if="showSuggestionsList && loadingSuggestions && query.trim()" 
          class="list-group-item bg-dark text-light border-secondary text-center p-2 position-absolute w-100 mt-1"
          style="z-index: 1000;"
        >
          {{ $t('search.loadingSuggestions') }}
        </div>
        <!-- No Suggestions Found Indicator -->
        <div 
          v-if="showSuggestionsList && !loadingSuggestions && suggestions.length === 0 && query.trim() && !error"
          class="list-group-item bg-dark text-light border-secondary text-center p-2 position-absolute w-100 mt-1"
          style="z-index: 1000;"
        >
          {{ $t('search.noSuggestions') }}
        </div>
      </div>
      <div class="col-md-2">
        <button type="submit" class="btn btn-primary w-100 py-2" :disabled="loadingFinalResults || (loadingSuggestions && query.trim())">
          {{ loadingFinalResults ? $t('search.button') : ((loadingSuggestions && query.trim()) ? $t('general.loading') : $t('search.button')) }}
        </button>
      </div>
    </form>

    <!-- Main Loading Indicator for Final Results -->
    <div v-if="loadingFinalResults" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">{{ $t('general.loading') }}</span>
      </div>
      <p class="mt-3 text-secondary">{{ $t('search.loadingResults') }}</p>
    </div>
    
    <!-- Error Display -->
    <div v-if="error && !loadingFinalResults" class="alert alert-danger" role="alert">
      {{ error }} <!-- Error messages from API might not need translation here, or could be generic keys -->
    </div>

    <!-- No Final Results Found -->
    <div v-if="!loadingFinalResults && searched && finalResults.length === 0 && !error && queryWhenSearched" class="text-center py-5 text-secondary">
      {{ $t('search.noResults', { query: queryWhenSearched }) }}
    </div>

    <!-- Final Results Display -->
    <div v-if="finalResults.length > 0 && !loadingFinalResults" class="row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4 row-cols-xl-5 g-4">
      <div v-for="movie in finalResults" :key="movie.id" class="col">
        <MovieCard :movie="movie" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n'; // Import useI18n
import { apiGet } from '@/utils/api';
import MovieCard from '@/components/MovieCard.vue'

const { t, locale } = useI18n(); // Initialize t and locale

const API_BASE_URL = '/api/tmdb';

const query = ref('');
const suggestions = ref([]);
const finalResults = ref([]); // Was: results
const loadingSuggestions = ref(false);
const loadingFinalResults = ref(false); // Was: loading
const showSuggestionsList = ref(false);
const error = ref(null); // Was: error = ref(false), changed to null for messages
const searched = ref(false);
const queryWhenSearched = ref('');
const router = useRouter();

let suggestionsDebounceTimer = null;
let internalQueryUpdate = false; // Flag to prevent watch from re-fetching suggestions on select

// Fetch suggestions as user types
async function fetchSuggestions(searchTerm) {
  if (!searchTerm.trim()) {
    suggestions.value = [];
    return;
  }
  loadingSuggestions.value = true;
  try {
    const lang = locale.value === 'en' ? 'en-US' : 'pt-BR';
    const data = await apiGet(`${API_BASE_URL}/search?query=${encodeURIComponent(searchTerm)}&page=1&language=${lang}`);
    suggestions.value = (data.results || []).slice(0, 7);
    if (query.value.trim()) {
        showSuggestionsList.value = true;
    }
  } catch (e) {
    console.error("Erro ao buscar sugestões:", e);
    suggestions.value = [];
    if (query.value.trim()) {
        showSuggestionsList.value = true;
    }
  } finally {
    loadingSuggestions.value = false;
  }
}

// Fetch final results when a suggestion is selected or search is triggered
async function fetchFinalResults(searchTerm) {
  if (!searchTerm.trim()) {
    finalResults.value = [];
    searched.value = true;
    queryWhenSearched.value = searchTerm;
    error.value = null; 
    return;
  }
  loadingFinalResults.value = true;
  error.value = null; 
  suggestions.value = []; 
  showSuggestionsList.value = false;

  try {
    const lang = locale.value === 'en' ? 'en-US' : 'pt-BR';
    const data = await apiGet(`${API_BASE_URL}/search?query=${encodeURIComponent(searchTerm)}&language=${lang}`);
    finalResults.value = data.results || [];
    searched.value = true;
    queryWhenSearched.value = searchTerm;
  } catch (e) {
    error.value = e.message || t('search.fetchError');
    console.error("Erro ao buscar filmes:", e);
    finalResults.value = [];
  } finally {
    loadingFinalResults.value = false;
  }
}

// Atualiza sugestões e resultados ao trocar idioma
watch(locale, () => {
  if (query.value.trim()) {
    fetchSuggestions(query.value);
    if (searched.value) {
      fetchFinalResults(query.value);
    }
  }
});

watch(query, (newQuery) => {
  if (internalQueryUpdate) {
    return;
  }
  clearTimeout(suggestionsDebounceTimer);

  if (!newQuery.trim()) {
    suggestions.value = [];
    finalResults.value = []; 
    showSuggestionsList.value = false;
    searched.value = false; 
    queryWhenSearched.value = ''; 
    loadingSuggestions.value = false;
    error.value = null; 
    return;
  }
  
  suggestionsDebounceTimer = setTimeout(() => {
    fetchSuggestions(newQuery);
  }, 300); // Debounce for suggestions
});

function selectSuggestion(movie) {
  internalQueryUpdate = true;
  query.value = movie.title;
  showSuggestionsList.value = false;
  suggestions.value = [];
  // Navega direto para a página de detalhes do filme
  router.push(`/movie/${movie.id}`);
  nextTick(() => {
    internalQueryUpdate = false;
  });
}

// Triggered by form submission (Enter or button click)
function triggerSearchNow() {
  clearTimeout(suggestionsDebounceTimer); 
  showSuggestionsList.value = false; 
  fetchFinalResults(query.value);
}

function handleInputFocus() {
  if (query.value.trim()) {
    showSuggestionsList.value = true; 
    if (suggestions.value.length === 0 && !loadingSuggestions.value) {
        clearTimeout(suggestionsDebounceTimer);
        fetchSuggestions(query.value); // Fetch immediately if input has text but no suggestions yet
    }
  }
}

function handleInputBlur() {
  setTimeout(() => {
    // A check can be added here if a suggestion item was the relatedTarget of the blur event
    // For simplicity, mousedown on items should handle selection before blur fully hides.
    showSuggestionsList.value = false;
  }, 150); 
}

function getPosterUrl(path) {
  return path ? `https://image.tmdb.org/t/p/w300${path}` : '';
}

function goToMovie(id) {
  router.push(`/movie/${id}`);
}
</script>

<style scoped>
/* Minimalist custom styles to complement Bootstrap */
.movie-card {
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.movie-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 20px rgba(var(--bs-primary-rgb), 0.3);
}

.poster-container {
  aspect-ratio: 2 / 3;
}

.movie-poster {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Styles for suggestion items */
.suggestion-item:hover {
  background-color: #495057; /* A slightly lighter dark shade for hover */
  cursor: pointer;
}

/* Mobile responsiveness is handled by Bootstrap's responsive classes */
</style>
