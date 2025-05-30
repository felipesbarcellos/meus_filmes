<template>
  <div v-if="recommendations.length > 0" class="mt-5">
    <h4 class="mb-3 text-primary">{{ $t('movieDetails.recommendations') }}</h4>
    <div class="row row-cols-2 row-cols-sm-3 row-cols-md-4 row-cols-lg-5 g-3">
      <div v-for="movie in recommendations" :key="movie.id" class="col">
        <MovieCard :movie="movie" />
      </div>
    </div>
  </div>
  <div v-else-if="loading" class="text-center py-4">
    <div class="spinner-border text-primary" role="status">
      <span class="visually-hidden">{{ $t('movieDetails.loading.srOnly') }}</span>
    </div>
    <p class="mt-2 text-secondary">{{ $t('movieDetails.loadingRecommendations') }}</p>
  </div>
  <div v-else-if="error" class="alert alert-danger text-center mt-3">{{ error }}</div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { apiGet } from '@/utils/api'
import MovieCard from './MovieCard.vue'

const props = defineProps({
  tmdbId: { type: [String, Number], required: true },
  language: { type: String, default: 'pt-BR' }
})
const { t, locale } = useI18n()
const recommendations = ref([])
const loading = ref(true)
const error = ref('')

async function fetchRecommendations() {
  loading.value = true
  error.value = ''
  try {
    const lang = locale.value === 'en' ? 'en-US' : 'pt-BR'
    const data = await apiGet(`/api/tmdb/movie/${props.tmdbId}/recommendations?language=${lang}`)
    recommendations.value = (data.results || []).slice(0, 10)
  } catch (e) {
    error.value = t('movieDetails.recommendationsError')
  } finally {
    loading.value = false
  }
}

onMounted(fetchRecommendations)
watch(() => props.tmdbId, fetchRecommendations)
watch(locale, fetchRecommendations)
</script>

<style scoped>
.row {
  margin-left: 0;
  margin-right: 0;
}
</style>
